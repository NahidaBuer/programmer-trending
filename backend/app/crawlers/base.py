from abc import ABC, abstractmethod
from typing import List, Optional, Any
from datetime import datetime
import asyncio
from dataclasses import dataclass

import httpx

from ..core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CrawledItem:
    """爬取到的条目数据结构"""

    source_id: str
    title: str
    url: str
    external_id: str  # 外部系统的唯一标识 (如 HN 的 item id)
    score: Optional[int] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    comments_count: Optional[int] = None
    tags: Optional[List[str]] = None


class BaseCrawler(ABC):
    """爬虫基类，定义了通用的爬取接口"""

    def __init__(self, source_id: str, source_name: str, base_url: str):
        self.source_id = source_id
        self.source_name = source_name
        self.base_url = base_url
        self.session: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ProgrammerTrending/1.0)"},
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """异步上下文管理器出口"""
        if self.session:
            await self.session.aclose()

    @abstractmethod
    async def fetch_hot_items(self, limit: int = 30) -> List[CrawledItem]:
        """
        抓取热门条目

        Args:
            limit: 抓取条目数量限制

        Returns:
            爬取到的条目列表
        """
        pass

    @abstractmethod
    async def fetch_item_details(self, external_id: str) -> Optional[CrawledItem]:
        """
        获取单个条目的详细信息

        Args:
            external_id: 外部系统的条目ID

        Returns:
            条目详细信息，如果不存在返回None
        """
        pass

    async def safe_request(self, url: str, **kwargs: Any) -> Optional[httpx.Response]:
        """
        安全的HTTP请求，包含重试和错误处理

        Args:
            url: 请求URL
            **kwargs: httpx.get()的额外参数

        Returns:
            响应对象或None（如果请求失败）
        """
        if not self.session:
            raise RuntimeError(
                "Crawler not initialized. Use 'async with' context manager."
            )

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = await self.session.get(url, **kwargs)
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"HTTP error {e.response.status_code} for {url}, attempt {attempt + 1}"
                )
                if e.response.status_code == 429:  # Too Many Requests
                    await asyncio.sleep(2**attempt)  # 指数退避
                elif attempt == max_retries - 1:
                    logger.error(
                        f"Failed to fetch {url} after {max_retries} attempts: {e}"
                    )
                    return None

            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.warning(f"Request error for {url}, attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error(
                        f"Failed to fetch {url} after {max_retries} attempts: {e}"
                    )
                    return None
                await asyncio.sleep(1)

        return None

    def validate_item(self, item: CrawledItem) -> bool:
        """
        验证爬取的条目数据是否有效

        Args:
            item: 爬取的条目

        Returns:
            是否有效
        """
        if not item.title or not item.title.strip():
            logger.warning(f"Invalid item: empty title for {item.external_id}")
            return False

        if not item.url or not item.url.startswith(("http://", "https://")):
            logger.warning(
                f"Invalid item: invalid URL {item.url} for {item.external_id}"
            )
            return False

        if not item.external_id:
            logger.warning("Invalid item: missing external_id")
            return False

        return True

    async def crawl_and_validate(self, limit: int = 30) -> List[CrawledItem]:
        """
        爬取并验证条目数据

        Args:
            limit: 抓取条目数量限制

        Returns:
            验证通过的条目列表
        """
        try:
            items = await self.fetch_hot_items(limit)
            valid_items = [item for item in items if self.validate_item(item)]

            logger.info(
                f"Crawled {len(items)} items from {self.source_name}, {len(valid_items)} valid"
            )

            return valid_items

        except Exception as e:
            logger.error(f"Failed to crawl from {self.source_name}: {e}")
            return []
