from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .common import PaginationMeta
from .summary import SummaryStatus


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


class ItemWithSummaryResponse(ItemBase):
    """带摘要信息的文章响应模型"""
    id: int = Field(..., description="条目ID")
    created_at: datetime = Field(..., description="创建时间")
    fetched_at: datetime = Field(..., description="抓取时间")
    
    # 摘要信息（可能为空）
    summary_content: Optional[str] = Field(None, description="AI摘要内容")
    translated_title: Optional[str] = Field(None, description="翻译后的标题")
    summary_status: Optional[SummaryStatus] = Field(None, description="摘要生成状态")

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    items: List[ItemResponse]
    pagination: PaginationMeta


class ItemWithSummaryListResponse(BaseModel):
    """带摘要信息的文章列表响应模型"""
    items: List[ItemWithSummaryResponse]
    pagination: PaginationMeta