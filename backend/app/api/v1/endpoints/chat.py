from fastapi import APIRouter, Request, HTTPException
from app.schemas.common import APIResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/", response_model=APIResponse[ChatResponse])
async def chat(
    request: Request,
    chat_request: ChatRequest
) -> APIResponse[ChatResponse]:
    """AI 对话接口"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        async with ai_service:
            success, result_data = await ai_service.generate_chat_response(
                message=chat_request.message,
                context_url=chat_request.context_url
            )
            
        if not success:
            raise HTTPException(
                status_code=500, 
                detail=f"AI service error: {result_data.get('error', 'Unknown error')}"
            )
            
        data = ChatResponse(
            reply=result_data["reply"],
            context_url=chat_request.context_url
        )
        
        return APIResponse(
            data=data,
            error=None,
            meta={"requestId": request_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))