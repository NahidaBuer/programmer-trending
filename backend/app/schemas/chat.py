from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """对话请求模型"""
    message: str = Field(..., description="用户消息")
    context_url: Optional[str] = Field(None, description="可选的上下文URL")


class ChatResponse(BaseModel):
    """对话响应模型"""
    reply: str = Field(..., description="AI回复内容")
    context_url: Optional[str] = Field(None, description="使用的上下文URL")