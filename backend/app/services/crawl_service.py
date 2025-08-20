from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from sqlalchemy import select, exists, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.database import AsyncSessionLocal
from ..core.config import get_settings
from ..models.source import Source
from ..models.item import Item
from ..models.summary import Summary, SummaryStatus  
from ..crawlers.base import BaseCrawler, CrawledItem
from ..crawlers.hackernews import HackerNewsCrawler

logger = logging.getLogger(__name__)


class CrawlService:
    """爬虫服务，负责协调多个爬虫和数据入库"""
    
    def __init__(self):
        self.crawlers: Dict[str, BaseCrawler] = {}
        self.settings = get_settings()
        self._register_crawlers()
        
    def _register_crawlers(self) -> None:
        """注册所有可用的爬虫"""
        # 注册 Hacker News 爬虫
        self.crawlers["hackernews"] = HackerNewsCrawler()
        
    async def ensure_sources_exist(self) -> None:
        """确保数据源存在于数据库中"""
        async with AsyncSessionLocal() as db:
            for source_id, crawler in self.crawlers.items():
                # 检查数据源是否存在
                stmt = select(exists().where(Source.id == source_id))
                result = await db.execute(stmt)
                source_exists = result.scalar()
                
                if not source_exists:
                    # 创建新的数据源记录
                    new_source = Source(
                        id=source_id,
                        name=crawler.source_name,
                        url=crawler.base_url,
                        enabled=True
                    )
                    db.add(new_source)
                    logger.info(f"Created new source: {crawler.source_name}")
                    
            await db.commit()
            
    async def crawl_single_source(self, source_id: str, limit: int = 30) -> List[Item]:
        """
        爬取单个数据源
        
        Args:
            source_id: 数据源ID
            limit: 抓取条目数量限制
            
        Returns:
            新创建的条目列表
        """
        if source_id not in self.crawlers:
            logger.error(f"Unknown source: {source_id}")
            return []
            
        crawler = self.crawlers[source_id]
        
        try:
            async with crawler:  # 使用上下文管理器
                # 爬取数据
                crawled_items = await crawler.crawl_and_validate(limit)
                logger.info(f"Crawled {len(crawled_items)} items from {source_id}")
                
                if not crawled_items:
                    return []
                
                # 保存到数据库
                new_items = await self._save_items_to_db(crawled_items)
                logger.info(f"Saved {len(new_items)} new items from {source_id}")
                
                return new_items
                
        except Exception as e:
            logger.error(f"Error crawling {source_id}: {e}")
            return []
    
    async def crawl_all_sources(self, limit_per_source: int = 30) -> Dict[str, List[Item]]:
        """
        爬取所有启用的数据源
        
        Args:
            limit_per_source: 每个数据源的抓取条目数量限制
            
        Returns:
            各数据源新创建的条目字典
        """
        # 确保数据源存在
        await self.ensure_sources_exist()
        
        # 获取启用的数据源
        enabled_sources = await self._get_enabled_sources()
        
        results = {}
        for source_id in enabled_sources:
            if source_id in self.crawlers:
                new_items = await self.crawl_single_source(source_id, limit_per_source)
                results[source_id] = new_items
            else:
                logger.warning(f"No crawler available for enabled source: {source_id}")
                
        return results
    
    async def _get_enabled_sources(self) -> List[str]:
        """获取启用的数据源列表"""
        async with AsyncSessionLocal() as db:
            stmt = select(Source.id).where(Source.enabled == True)  # noqa: E712
            result = await db.execute(stmt)
            return [row[0] for row in result]
    
    async def _save_items_to_db(self, crawled_items: List[CrawledItem]) -> List[Item]:
        """
        将爬取的条目保存到数据库
        
        Args:
            crawled_items: 爬取的条目列表
            
        Returns:
            新创建的数据库条目列表
        """
        if not crawled_items:
            return []
            
        async with AsyncSessionLocal() as db:
            new_items = []
            
            for crawled_item in crawled_items:
                try:
                    # 检查条目是否已存在（基于 source_id + external_id）
                    stmt = select(exists().where(
                        (Item.source_id == crawled_item.source_id) &
                        (Item.external_id == crawled_item.external_id)
                    ))
                    result = await db.execute(stmt)
                    item_exists = result.scalar()
                    
                    if item_exists:
                        logger.debug(f"Item {crawled_item.external_id} already exists, skipping")
                        continue
                        
                    # 创建新的条目
                    new_item = Item(
                        source_id=crawled_item.source_id,
                        title=crawled_item.title,
                        url=crawled_item.url,
                        external_id=crawled_item.external_id,
                        score=crawled_item.score,
                        author=crawled_item.author,
                        created_at=crawled_item.created_at or datetime.utcnow(),
                        fetched_at=datetime.utcnow(),
                        comments_count=crawled_item.comments_count,
                        tags=crawled_item.tags or []
                    )
                    
                    db.add(new_item)
                    new_items.append(new_item)
                    
                except Exception as e:
                    logger.error(f"Error saving item {crawled_item.external_id}: {e}")
                    continue
                    
            # 提交所有更改
            await db.commit()
            
            # 刷新对象以获取生成的ID
            for item in new_items:
                await db.refresh(item)
                
            # 为新文章创建摘要任务
            await self._create_summary_tasks(db, new_items)
                
            logger.info(f"Successfully saved {len(new_items)} new items to database")
            return new_items
    
    async def get_recent_items(self, source_id: Optional[str] = None, limit: int = 50) -> List[Item]:
        """
        获取最近的条目
        
        Args:
            source_id: 可选的数据源过滤
            limit: 返回条目数量限制
            
        Returns:
            最近的条目列表
        """
        async with AsyncSessionLocal() as db:
            stmt = select(Item).order_by(Item.fetched_at.desc())
            
            if source_id:
                stmt = stmt.where(Item.source_id == source_id)
                
            stmt = stmt.limit(limit)
            
            result = await db.execute(stmt)
            return list(result.scalars().all())
    
    async def get_crawl_stats(self) -> Dict[str, Any]:
        """
        获取爬虫统计信息
        
        Returns:
            包含各种统计信息的字典
        """
        async with AsyncSessionLocal() as db:
            stats = {}
            
            # 总条目数
            total_stmt = select(func.count(Item.id))
            result = await db.execute(total_stmt)
            stats["total_items"] = result.scalar()
            
            # 各数据源条目数
            source_stats_stmt = select(
                Item.source_id,
                func.count(Item.id).label("count")
            ).group_by(Item.source_id)
            
            result = await db.execute(source_stats_stmt)
            stats["by_source"] = {row.source_id: row.count for row in result}
            
            # 最近24小时的条目数
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_stmt = select(func.count(Item.id)).where(Item.fetched_at >= yesterday)
            result = await db.execute(recent_stmt)
            stats["last_24h"] = result.scalar()
            
            return stats
    
    async def _create_summary_tasks(self, db: AsyncSession, items: List[Item]) -> None:
        """为新文章创建摘要任务"""
        if not items:
            return
            
        try:
            summary_tasks = []
            for item in items:
                # 检查是否已存在摘要
                existing = await db.execute(
                    select(Summary).where(Summary.item_id == item.id)
                )
                if existing.first():
                    continue
                    
                # 创建摘要任务
                summary = Summary(
                    item_id=item.id,
                    model=self.settings.gemini_model,
                    lang="zh-CN",
                    status=SummaryStatus.PENDING,
                    retry_count=0,
                    max_retries=self.settings.ai_summary_max_retries
                )
                summary_tasks.append(summary)
                
            if summary_tasks:
                db.add_all(summary_tasks)
                await db.commit()
                logger.info(f"Created {len(summary_tasks)} summary tasks for new items")
                
        except Exception as e:
            logger.error(f"Error creating summary tasks: {e}")
            await db.rollback()


# 全局爬虫服务实例
crawl_service = CrawlService()