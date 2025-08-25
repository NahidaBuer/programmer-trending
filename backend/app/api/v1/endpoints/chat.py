"""
流式聊天 API 端点

支持匿名用户（限流）和用户自己API key两种模式
"""
from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import StreamingResponse
import json
from app.services.chat_service import chat_service, ChatRequest
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/stream")
async def chat_stream_anonymous(
    request: Request,
    chat_request: ChatRequest
) -> StreamingResponse:
    """匿名用户流式聊天接口（使用服务器API key + 全站限流）"""
    
    async def generate():
        try:
            async for chunk in chat_service.stream_chat_anonymous(chat_request):
                logger.info(f"chunk: {chunk}")
                yield chunk
        except Exception as e:
            # 错误处理
            error_data = json.dumps({"error": f"服务器错误: {str(e)}"})
            yield f'data: {error_data}\n\n'
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.post("/stream/user-key")
async def chat_stream_with_user_key(
    request: Request,
    chat_request: ChatRequest,
    x_api_key: str = Header(alias="X-API-Key")
) -> StreamingResponse:
    """用户自己API key的流式聊天接口（无限流）"""
    
    if not x_api_key:
        raise HTTPException(
            status_code=400, 
            detail="Missing X-API-Key header"
        )
    
    async def generate():
        try:
            async for chunk in chat_service.stream_chat_with_user_key(chat_request, x_api_key):
                yield chunk
        except Exception as e:
            # 错误处理
            error_data = json.dumps({"error": f"服务器错误: {str(e)}"})
            yield f'data: {error_data}\n\n'
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.get("/limits")
async def get_rate_limits(request: Request):
    """获取当前限流状态"""
    # 简单返回限制信息
    return {
        "global_limit": "5 requests per 10 minutes",
    }