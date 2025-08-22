"""
异步摘要生成任务模块

使用队列和并发控制机制生成文章摘要
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.database import AsyncSessionLocal
from ..models.item import Item
from ..models.summary import Summary, SummaryStatus
from ..services.ai_service import ai_service

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """异步摘要生成器"""
    
    def __init__(self):
        self.settings = get_settings()
        # 使用信号量控制并发度
        self.semaphore = asyncio.Semaphore(self.settings.summary_concurrency)
        self.is_running = False
        
    async def start_generation_cycle(self) -> None:
        """启动一轮摘要生成循环"""
        if self.is_running:
            logger.info("Summary generation already running, skipping")
            return
            
        self.is_running = True
        try:
            logger.info("Starting summary generation cycle")
            
            async with AsyncSessionLocal() as session:
                # 获取待处理的摘要任务
                pending_summaries = await self._get_pending_summaries(session)
                
                if not pending_summaries:
                    logger.info("No pending summaries found")
                    return
                    
                logger.info(f"Found {len(pending_summaries)} pending summaries")
                
                # 并发生成摘要
                tasks = [
                    self._generate_single_summary(summary_id)
                    for summary_id in pending_summaries
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 统计结果
                success_count = sum(1 for r in results if r is True)
                error_count = sum(1 for r in results if isinstance(r, Exception))
                
                logger.info(f"Generation cycle completed: {success_count} success, {error_count} errors")
                
        except Exception as e:
            logger.error(f"Error in summary generation cycle: {e}")
        finally:
            self.is_running = False
            
    async def _get_pending_summaries(self, session: AsyncSession) -> List[int]:
        """获取待处理的摘要ID列表"""
        stmt = select(Summary.id).where(
            Summary.status.in_([SummaryStatus.PENDING, SummaryStatus.FAILED])
        ).where(
            Summary.retry_count < Summary.max_retries
        ).order_by(Summary.created_at)
        
        result = await session.execute(stmt)
        return [row[0] for row in result.fetchall()]
        
    async def _generate_single_summary(self, summary_id: int) -> bool:
        """生成单个摘要（带并发控制）"""
        async with self.semaphore:
            logger.info(f"Generating summary for {summary_id}")
            result = await self._process_summary(summary_id)
            
            # 为了避免突破速率限制，在任务之间添加短暂延迟
            # 当前配置为每分钟10个请求，所以至少间隔6秒
            if self.settings.ai_enable_rate_limiting:
                delay = 60 / self.settings.ai_rate_limit_per_minute + 1  # 添加1秒缓冲
                logger.debug(f"Waiting {delay} seconds before next summary generation")
                await asyncio.sleep(delay)
            
            return result
            
    async def _process_summary(self, summary_id: int) -> bool:
        """处理单个摘要生成"""
        try:
            async with AsyncSessionLocal() as session:
                # 获取摘要记录和关联的文章
                stmt = select(Summary, Item).join(Item, Summary.item_id == Item.id).where(Summary.id == summary_id)
                result = await session.execute(stmt)
                row = result.first()
                
                if not row:
                    logger.error(f"Summary {summary_id} not found")
                    return False
                    
                summary, item = row
                
                # 检查状态是否可以处理
                if summary.status not in [SummaryStatus.PENDING, SummaryStatus.FAILED]:
                    logger.info(f"Summary {summary_id} status is {summary.status}, skipping")
                    return True
                    
                # 检查重试次数
                if summary.retry_count >= summary.max_retries:
                    await self._mark_permanently_failed(session, summary)
                    return False
                    
                # 更新状态为进行中
                await self._update_summary_status(
                    session, summary,
                    status=SummaryStatus.IN_PROGRESS,
                    started_at=datetime.now(timezone.utc)
                )
                await session.commit()
                
                # 生成摘要
                async with ai_service:
                    success, result_data = await ai_service.generate_summary(item)
                    
                if success:
                    # 成功：更新摘要内容
                    await self._update_summary_success(session, summary, result_data)
                    logger.info(f"Successfully generated summary for item {item.id}")
                    return True
                else:
                    # 失败：增加重试次数
                    await self._update_summary_failure(session, summary, result_data)
                    logger.error(f"Failed to generate summary for item {item.id}: {result_data.get('error')}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error processing summary {summary_id}: {e}")
            # 尝试更新失败状态
            try:
                async with AsyncSessionLocal() as session:
                    summary = await session.get(Summary, summary_id)
                    if summary:
                        await self._update_summary_failure(session, summary, {"error": str(e)})
            except Exception as e2:
                logger.error(f"Failed to update error status for summary {summary_id}: {e2}")
            return False
            
    async def _update_summary_status(
        self, 
        session: AsyncSession, 
        summary: Summary,
        status: SummaryStatus,
        started_at: Optional[datetime] = None
    ) -> None:
        """更新摘要状态"""
        update_data: dict[str, Any] = {"status": status}
        if started_at:
            update_data["started_at"] = started_at
            
        stmt = update(Summary).where(Summary.id == summary.id).values(**update_data)
        await session.execute(stmt)
        
    async def _update_summary_success(
        self,
        session: AsyncSession,
        summary: Summary,
        result_data: dict[str, Any]
    ) -> None:
        """更新摘要成功状态"""
        now = datetime.now(timezone.utc)
        stmt = update(Summary).where(Summary.id == summary.id).values(
            status=SummaryStatus.COMPLETED,
            content=result_data.get("content"),
            translated_title=result_data.get("translated_title"),
            completed_at=now,
            generation_duration_ms=result_data.get("generation_duration_ms"),
            url_retrieval_status=result_data.get("url_retrieval_status"),
            response_json=result_data.get("response_json"),
            error_message=None,  # 清除之前的错误信息
            error_type=None
        )
        await session.execute(stmt)
        await session.commit()
        
    async def _update_summary_failure(
        self,
        session: AsyncSession,
        summary: Summary,
        result_data: dict[str, Any]
    ) -> None:
        """更新摘要失败状态"""
        now = datetime.now(timezone.utc)
        new_retry_count = summary.retry_count + 1
        
        # 判断是否达到最大重试次数
        if new_retry_count >= summary.max_retries:
            status = SummaryStatus.PERMANENTLY_FAILED
        else:
            status = SummaryStatus.FAILED
            
        stmt = update(Summary).where(Summary.id == summary.id).values(
            status=status,
            retry_count=new_retry_count,
            last_retry_at=now,
            error_message=result_data.get("error"),
            error_type=self._classify_error(result_data.get("error", "")),
            generation_duration_ms=result_data.get("generation_duration_ms"),
            response_json=result_data.get("response_json")
        )
        await session.execute(stmt)
        await session.commit()
        
    async def _mark_permanently_failed(
        self,
        session: AsyncSession,
        summary: Summary
    ) -> None:
        """标记为永久失败"""
        stmt = update(Summary).where(Summary.id == summary.id).values(
            status=SummaryStatus.PERMANENTLY_FAILED
        )
        await session.execute(stmt)
        await session.commit()
        
    def _classify_error(self, error_message: str) -> str:
        """分类错误类型"""
        error_lower = error_message.lower()
        
        if "timeout" in error_lower or "connection" in error_lower:
            return "NETWORK_ERROR"
        elif "api key" in error_lower or "unauthorized" in error_lower:
            return "AUTH_ERROR"
        elif "api error" in error_lower or "status code" in error_lower:
            return "API_ERROR"
        elif "url" in error_lower or "retrieval" in error_lower:
            return "CONTENT_ERROR"
        else:
            return "UNKNOWN_ERROR"
            
    async def create_summary_task(
        self,
        item_id: int,
        model: str = "gemini-2.5-flash",
        lang: str = "zh-CN"
    ) -> Optional[Summary]:
        """为文章创建摘要任务"""
        if not model:
            model = self.settings.gemini_model
            
        try:
            async with AsyncSessionLocal() as session:
                # 检查是否已存在摘要
                existing = await session.execute(
                    select(Summary).where(Summary.item_id == item_id)
                )
                if existing.first():
                    logger.info(f"Summary already exists for item {item_id}")
                    return None
                    
                # 创建新摘要任务
                summary = Summary(
                    item_id=item_id,
                    model=model,
                    lang=lang,
                    status=SummaryStatus.PENDING,
                    created_at=func.now(),
                    retry_count=0,
                    max_retries=self.settings.ai_summary_max_retries
                )
                
                session.add(summary)
                await session.commit()
                await session.refresh(summary)
                
                logger.info(f"Created summary task {summary.id} for item {item_id}")
                return summary
                
        except Exception as e:
            logger.error(f"Error creating summary task for item {item_id}: {e}")
            return None
    
    async def create_summary_tasks_for_missing_items(
        self,
        source_id: Optional[str] = None,
        model: str = "gemini-2.5-flash", 
        lang: str = "zh-CN"
    ) -> dict[str, Any]:
        """为所有没有摘要的文章批量创建摘要任务"""
        if not model:
            model = self.settings.gemini_model
            
        try:
            async with AsyncSessionLocal() as session:
                # 查找所有没有摘要的文章 
                subquery = select(Summary.id).where(Summary.item_id == Item.id).exists()
                stmt = select(Item.id).where(~subquery)
                
                # 如果指定了数据源，只处理该数据源的文章
                if source_id:
                    stmt = stmt.where(Item.source_id == source_id)
                
                result = await session.execute(stmt)
                missing_item_ids = [row[0] for row in result.fetchall()]
                
                if not missing_item_ids:
                    logger.info("未找到没有摘要的文章")
                    return {"created_count": 0, "total_missing": 0}
                
                logger.info(f"找到 {len(missing_item_ids)} 篇文章没有摘要")
                
                # 批量创建摘要任务
                summary_tasks: List[Summary] = []
                for item_id in missing_item_ids:
                    summary = Summary(
                        item_id=item_id,
                        model=model,
                        lang=lang,
                        status=SummaryStatus.PENDING,
                        created_at=func.now(),
                        retry_count=0,
                        max_retries=self.settings.ai_summary_max_retries
                    )
                    summary_tasks.append(summary)
                
                session.add_all(summary_tasks)
                await session.commit()
                
                created_count = len(summary_tasks)
                logger.info(f"创建了 {created_count} 个摘要任务")
                
                return {
                    "created_count": created_count,
                    "total_missing": len(missing_item_ids),
                    "source_id": source_id
                }
                
        except Exception as e:
            logger.error(f"创建摘要任务失败: {e}")
            return {"created_count": 0, "total_missing": 0, "error": str(e)}


# 全局摘要生成器实例
summary_generator = SummaryGenerator()