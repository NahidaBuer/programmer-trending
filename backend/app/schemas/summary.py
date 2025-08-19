from datetime import datetime
from pydantic import BaseModel, Field


class SummaryBase(BaseModel):
    item_id: int = Field(..., description="关联的文章ID")
    model: str = Field(..., description="AI 模型名称")
    lang: str = Field(default="zh-CN", description="语言")
    content: str = Field(..., description="摘要内容")


class SummaryCreate(SummaryBase):
    pass


class Summary(SummaryBase):
    id: int = Field(..., description="摘要ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True