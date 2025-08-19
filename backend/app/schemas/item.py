from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .common import PaginationMeta


class ItemBase(BaseModel):
    source_id: str = Field(..., description="数据源ID")
    title: str = Field(..., description="文章标题")
    url: str = Field(..., description="文章链接")
    score: Optional[int] = Field(None, description="分数")
    author: Optional[str] = Field(None, description="作者")


class ItemCreate(ItemBase):
    created_at: Optional[datetime] = Field(None, description="创建时间")
    fetched_at: Optional[datetime] = Field(None, description="抓取时间")


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    score: Optional[int] = None
    author: Optional[str] = None


class ItemResponse(ItemBase):
    id: int = Field(..., description="条目ID")
    created_at: datetime = Field(..., description="创建时间")
    fetched_at: datetime = Field(..., description="抓取时间")

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    items: List[ItemResponse]
    pagination: PaginationMeta