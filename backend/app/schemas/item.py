from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .summary import Summary


class ItemBase(BaseModel):
    source_id: str = Field(..., description="数据源ID")
    title: str = Field(..., description="文章标题")
    url: str = Field(..., description="文章链接")
    score: Optional[int] = Field(None, description="分数")
    author: Optional[str] = Field(None, description="作者")


class ItemCreate(ItemBase):
    created_at: Optional[datetime] = Field(None, description="创建时间")
    fetched_at: Optional[datetime] = Field(None, description="抓取时间")


class Item(ItemBase):
    id: int = Field(..., description="条目ID")
    created_at: datetime = Field(..., description="创建时间")
    fetched_at: datetime = Field(..., description="抓取时间")
    summary: Optional[Summary] = Field(None, description="AI 摘要")

    class Config:
        from_attributes = True