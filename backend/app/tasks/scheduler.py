import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
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
            logger.info("Task scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self) -> None:
        """停止调度器"""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("Task scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            
    async def _add_crawl_jobs(self) -> None:
        """添加爬取任务"""
        # 定期爬取所有数据源
        crawl_interval = self.settings.crawl_interval_minutes
        
        self.scheduler.add_job(
            self.crawl_all_sources_job,
            trigger=IntervalTrigger(minutes=crawl_interval),
            id="crawl_all_sources",
            name="Crawl All Sources",
            max_instances=1,  # 防止重复执行
            replace_existing=True,
            next_run_time=datetime.now() + timedelta(seconds=30),  # 30秒后开始首次执行
        )
        
        # 定期生成摘要（每15分钟执行一次）
        self.scheduler.add_job(
            self.generate_summaries_job,
            trigger=IntervalTrigger(minutes=15),
            id="generate_summaries",
            name="Generate AI Summaries",
            max_instances=1,  # 防止重复执行
            replace_existing=True,
            next_run_time=datetime.now() + timedelta(minutes=2),  # 2分钟后开始首次执行
        )
        
        logger.info(f"Added crawl job with {crawl_interval} minute interval")
        logger.info("Added summary generation job with 15 minute interval")
        
    async def crawl_all_sources_job(self) -> None:
        """爬取所有数据源的定时任务"""
        try:
            logger.info("Starting scheduled crawl of all sources")
            start_time = datetime.now()
            
            results = await crawl_service.crawl_all_sources(limit_per_source=30)
            
            # 统计结果
            total_new_items = sum(len(items) for items in results.values())
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"Crawl completed: {total_new_items} new items from "
                f"{len(results)} sources in {duration:.2f}s"
            )
            
            # 记录各数据源的统计
            for source_id, items in results.items():
                logger.info(f"  {source_id}: {len(items)} new items")
                
        except Exception as e:
            logger.error(f"Scheduled crawl failed: {e}")
            
    async def generate_summaries_job(self) -> None:
        """生成摘要的定时任务"""
        try:
            logger.info("Starting scheduled summary generation")
            start_time = datetime.now()
            
            await summary_generator.start_generation_cycle()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Summary generation completed in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Scheduled summary generation failed: {e}")
            
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
                logger.info(f"Manual crawl triggered for source: {source_id}")
                new_items = await crawl_service.crawl_single_source(source_id)
                results = {source_id: new_items}
            else:
                logger.info("Manual crawl triggered for all sources")
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
            logger.error(f"Manual crawl failed: {e}")
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
            logger.info("Manual summary generation triggered")
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
            logger.error(f"Manual summary generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": 0,
                "message": "Summary generation failed"
            }
    
    def get_job_status(self) -> Dict[str, Any]:
        """获取任务状态信息"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
            
        return {
            "scheduler_running": self.scheduler.running,
            "jobs": jobs
        }


# 全局调度器实例
task_scheduler = TaskScheduler()