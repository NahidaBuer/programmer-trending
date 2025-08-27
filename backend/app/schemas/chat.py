from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """对话请求模型"""

    message: str = Field(..., description="用户消息")


class ChatResponse(BaseModel):
    """对话响应模型"""

    reply: str = Field(..., description="AI回复内容")
