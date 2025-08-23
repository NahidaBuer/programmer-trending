from datetime import datetime
from typing import List, Optional

from .base import BaseCrawler, CrawledItem
from ..core.logging import get_logger

logger = get_logger(__name__)


class HackerNewsCrawler(BaseCrawler):
    """Hacker News 官方 API 爬虫"""
    
    def __init__(self):
        super().__init__(
            source_id="hackernews",
            source_name="Hacker News",
            base_url="https://hacker-news.firebaseio.com/v0"
        )
    
    async def fetch_hot_items(self, limit: int = 30) -> List[CrawledItem]:
        """
        获取 HN 热门故事
        
        Args:
            limit: 获取条目数量限制
            
        Returns:
            爬取到的条目列表
        """
        try:
            # 获取 topstories 列表
            top_stories_url = f"{self.base_url}/topstories.json"
            response = await self.safe_request(top_stories_url)
            
            if not response:
                logger.error("Failed to fetch top stories list")
                return []
                
            story_ids = response.json()[:limit]  # 取前 limit 个
            logger.info(f"Got {len(story_ids)} story IDs from HN")
            
            # 并发获取每个故事的详情
            items = []
            for story_id in story_ids:
                item = await self.fetch_item_details(str(story_id))
                if item:
                    items.append(item)
                    
            return items
            
        except Exception as e:
            logger.error(f"Error fetching HN hot items: {e}")
            return []
    
    async def fetch_item_details(self, external_id: str) -> Optional[CrawledItem]:
        """
        获取单个 HN 条目详情
        
        Args:
            external_id: HN 条目 ID
            
        Returns:
            条目详情或 None
        """
        try:
            item_url = f"{self.base_url}/item/{external_id}.json"
            response = await self.safe_request(item_url)
            
            if not response:
                logger.warning(f"Failed to fetch item {external_id}")
                return None
                
            data = response.json()
            
            # 检查是否是有效的 story 类型
            if data.get("type") != "story":
                logger.debug(f"Skipping non-story item {external_id}: type={data.get('type')}")
                return None
                
            # 确保有标题和URL
            title = data.get("title")
            url = data.get("url")
            
            if not title:
                logger.warning(f"Story {external_id} has no title")
                return None
                
            # 如果没有外部URL，使用HN的讨论链接
            if not url:
                url = f"https://news.ycombinator.com/item?id={external_id}"
                
            # 构造 CrawledItem
            item = CrawledItem(
                source_id=self.source_id,
                title=title,
                url=url,
                external_id=external_id,
                score=data.get("score"),
                author=data.get("by"),
                created_at=datetime.fromtimestamp(data["time"]) if "time" in data else None,
                comments_count=data.get("descendants"),
            )
            
            return item
            
        except Exception as e:
            logger.error(f"Error fetching HN item {external_id}: {e}")
            return None
    
    async def fetch_ask_stories(self, limit: int = 20) -> List[CrawledItem]:
        """
        获取 Ask HN 故事
        
        Args:
            limit: 获取条目数量限制
            
        Returns:
            爬取到的 Ask HN 条目列表
        """
        try:
            ask_stories_url = f"{self.base_url}/askstories.json"
            response = await self.safe_request(ask_stories_url)
            
            if not response:
                logger.error("Failed to fetch ask stories list")
                return []
                
            story_ids = response.json()[:limit]
            logger.info(f"Got {len(story_ids)} Ask HN story IDs")
            
            # 并发获取每个故事的详情
            items = []
            for story_id in story_ids:
                item = await self.fetch_item_details(str(story_id))
                if item:
                    # 为 Ask HN 添加标签
                    if not item.tags:
                        item.tags = []
                    item.tags.append("ask-hn")
                    items.append(item)
                    
            return items
            
        except Exception as e:
            logger.error(f"Error fetching Ask HN stories: {e}")
            return []
    
    async def fetch_show_stories(self, limit: int = 20) -> List[CrawledItem]:
        """
        获取 Show HN 故事
        
        Args:
            limit: 获取条目数量限制
            
        Returns:
            爬取到的 Show HN 条目列表
        """
        try:
            show_stories_url = f"{self.base_url}/showstories.json"
            response = await self.safe_request(show_stories_url)
            
            if not response:
                logger.error("Failed to fetch show stories list")
                return []
                
            story_ids = response.json()[:limit]
            logger.info(f"Got {len(story_ids)} Show HN story IDs")
            
            # 并发获取每个故事的详情
            items = []
            for story_id in story_ids:
                item = await self.fetch_item_details(str(story_id))
                if item:
                    # 为 Show HN 添加标签
                    if not item.tags:
                        item.tags = []
                    item.tags.append("show-hn")
                    items.append(item)
                    
            return items
            
        except Exception as e:
            logger.error(f"Error fetching Show HN stories: {e}")
            return []