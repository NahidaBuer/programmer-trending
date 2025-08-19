from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse
from app.schemas.source import SourceResponse

router = APIRouter()


@router.get("/", response_model=APIResponse[List[SourceResponse]])
async def get_sources(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[List[SourceResponse]]:
    """获取数据源列表"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    # TODO: 实现获取数据源逻辑
    return APIResponse(
        data=[],
        error=None,
        meta={"requestId": request_id}
    )