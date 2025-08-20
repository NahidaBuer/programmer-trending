from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class SummaryStatus(str, Enum):
    """摘要生成状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    PERMANENTLY_FAILED = "permanently_failed"
    SKIPPED = "skipped"


class SummaryBase(BaseModel):
    item_id: int = Field(..., description="关联的文章ID")
    model: str = Field(..., description="AI 模型名称")
    lang: str = Field(default="zh-CN", description="语言")


class SummaryCreate(SummaryBase):
    content: Optional[str] = None
    status: SummaryStatus = SummaryStatus.PENDING
    max_retries: int = Field(default=3, description="最大重试次数")


class SummaryUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[SummaryStatus] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    generation_duration_ms: Optional[int] = None
    url_retrieval_status: Optional[str] = None
    response_json: Optional[Dict[str, Any]] = None


class SummaryResponse(BaseModel):
    id: int = Field(..., description="摘要ID")
    item_id: int = Field(..., description="关联的文章ID")
    model: str = Field(..., description="AI 模型名称")
    lang: str = Field(..., description="语言")
    content: Optional[str] = Field(None, description="摘要内容")
    status: SummaryStatus = Field(..., description="生成状态")
    retry_count: int = Field(..., description="重试次数")
    max_retries: int = Field(..., description="最大重试次数")
    created_at: datetime = Field(..., description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始生成时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    generation_duration_ms: Optional[int] = Field(None, description="生成耗时")
    url_retrieval_status: Optional[str] = Field(None, description="URL检索状态")

    class Config:
        from_attributes = True