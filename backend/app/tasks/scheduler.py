import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from ..core.config import get_settings
from ..services.crawl_service import crawl_service
from .summary_generator import summary_generator

logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器，管理定时爬取任务"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.settings = get_settings()
        self._setup_event_listeners()
        
    def _setup_event_listeners(self) -> None:
        """设置事件监听器"""
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        
    def _job_executed(self, event) -> None:
        """任务执行成功时的回调"""
        logger.info(f"Job {event.job_id} executed successfully at {datetime.now()}")
        
    def _job_error(self, event) -> None:
        """任务执行失败时的回调"""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
        
    async def start(self) -> None:
        """启动调度器"""
        try:
            # 添加定时任务
            await self._add_crawl_jobs()
            
            # 启动调度器
            self.scheduler.start()
            logger.info("调度器启动成功")
            
        except Exception as e:
            logger.error(f"启动调度器失败: {e}")
            raise
    
    async def stop(self) -> None:
        """停止调度器"""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("调度器停止成功")
        except Exception as e:
            logger.error(f"停止调度器失败: {e}")
            
    async def _add_crawl_jobs(self) -> None:
        """添加爬取任务"""
        crawl_interval = self.settings.crawl_interval_minutes
        added_jobs: list[str] = []
        
        # 根据配置添加定时爬虫任务
        if self.settings.enable_crawl_scheduler:
            self.scheduler.add_job(
                self.crawl_all_sources_job,
                trigger=IntervalTrigger(minutes=crawl_interval),
                id="crawl_all_sources",
                name="Crawl All Sources",
                max_instances=1,  # 防止重复执行
                replace_existing=True,
                next_run_time=datetime.now() + timedelta(seconds=30),  # 30秒后开始首次执行
            )
            added_jobs.append(f"爬取任务 (间隔 {crawl_interval} 分钟)")
            logger.info(f"✅ 已启用定时爬虫任务，间隔 {crawl_interval} 分钟")
        else:
            logger.info("❌ 定时爬虫任务已禁用 (ENABLE_CRAWL_SCHEDULER=false)")
        
        # 根据配置添加定时摘要生成任务
        if self.settings.enable_summary_scheduler:
            self.scheduler.add_job(
                self.generate_summaries_job,
                trigger=IntervalTrigger(minutes=crawl_interval),
                id="generate_summaries", 
                name="Generate AI Summaries",
                max_instances=1,  # 防止重复执行
                replace_existing=True,
                next_run_time=datetime.now() + timedelta(minutes=2),  # 2分钟后开始首次执行
            )
            added_jobs.append(f"摘要生成任务 (间隔 {crawl_interval} 分钟)")
            logger.info(f"✅ 已启用定时AI摘要任务，间隔 {crawl_interval} 分钟")
        else:
            logger.info("❌ 定时AI摘要任务已禁用 (ENABLE_SUMMARY_SCHEDULER=false)")
        
        # 汇总信息
        if added_jobs:
            logger.info(f"📅 已添加定时任务: {', '.join(added_jobs)}")
        else:
            logger.warning("⚠️  所有定时任务都已禁用，调度器将空运行")
        
    async def crawl_all_sources_job(self) -> None:
        """爬取所有数据源的定时任务"""
        try:
            logger.info("开始定时爬取所有数据源")
            start_time = datetime.now()
            
            results = await crawl_service.crawl_all_sources(limit_per_source=30)
            
            # 统计结果
            total_new_items = sum(len(items) for items in results.values())
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"爬取完成: {total_new_items} 个新文章来自 "
                f"{len(results)} 个数据源，耗时 {duration:.2f} 秒"
            )
            
            # 记录各数据源的统计
            for source_id, items in results.items():
                logger.info(f"  {source_id}: {len(items)} 个新文章")
                
        except Exception as e:
            logger.error(f"定时爬取失败: {e}")
            
    async def generate_summaries_job(self) -> None:
        """生成摘要的定时任务"""
        try:
            logger.info("开始定时生成摘要")
            start_time = datetime.now()
            
            await summary_generator.start_generation_cycle()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"摘要生成完成，耗时 {duration:.2f} 秒")
            
        except Exception as e:
            logger.error(f"定时生成摘要失败: {e}")
            
    async def trigger_manual_crawl(self, source_id: str | None = None) -> Dict[str, Any]:
        """
        手动触发爬取任务
        
        Args:
            source_id: 可选的特定数据源ID，为None时爬取所有源
            
        Returns:
            执行结果统计
        """
        try:
            start_time = datetime.now()
            
            if source_id:
                logger.info(f"手动触发爬取任务，数据源: {source_id}")
                new_items = await crawl_service.crawl_single_source(source_id)
                results = {source_id: new_items}
            else:
                logger.info("手动触发爬取任务，所有数据源")
                results = await crawl_service.crawl_all_sources()
                
            total_new_items = sum(len(items) for items in results.values())
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "total_new_items": total_new_items,
                "duration_seconds": duration,
                "sources_crawled": len(results),
                "details": {
                    source: len(items) for source, items in results.items()
                }
            }
            
        except Exception as e:
            logger.error(f"手动触发爬取任务失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_new_items": 0,
                "duration_seconds": 0,
                "sources_crawled": 0,
                "details": {}
            }
            
    async def trigger_manual_summary_generation(self) -> Dict[str, Any]:
        """
        手动触发摘要生成任务
        
        Returns:
            执行结果统计
        """
        try:
            logger.info("手动触发摘要生成任务")
            start_time = datetime.now()
            
            await summary_generator.start_generation_cycle()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "duration_seconds": duration,
                "message": "Summary generation completed"
            }
            
        except Exception as e:
            logger.error(f"手动触发摘要生成任务失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": 0,
                "message": "Summary generation failed"
            }
    
    def get_job_status(self) -> Dict[str, Any]:
        """获取任务状态信息"""
        jobs: list[dict[str, Any]] = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
            
        return {
            "scheduler_running": self.scheduler.running,
            "jobs": jobs,
            "configuration": {
                "crawl_scheduler_enabled": self.settings.enable_crawl_scheduler,
                "summary_scheduler_enabled": self.settings.enable_summary_scheduler,
                "crawl_interval_minutes": self.settings.crawl_interval_minutes,
                "summary_concurrency": self.settings.summary_concurrency,
            }
        }


# 全局调度器实例
task_scheduler = TaskScheduler()