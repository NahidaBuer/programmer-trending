from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse, PaginationMeta
from app.schemas.item import ItemResponse, ItemListResponse

router = APIRouter()


@router.get("/", response_model=APIResponse[ItemListResponse])
async def get_items(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条目数"),
    source_id: Optional[int] = Query(None, description="数据源ID"),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[ItemListResponse]:
    """获取热榜条目列表"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    # TODO: 实现获取条目列表逻辑
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total=0,
        total_pages=0,
        has_next=False,
        has_prev=False
    )
    
    return APIResponse(
        data=ItemListResponse(items=[], pagination=pagination),
        error=None,
        meta={"requestId": request_id}
    )


@router.get("/{item_id}", response_model=APIResponse[ItemResponse])
async def get_item(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[ItemResponse]:
    """获取单个条目详情"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    # TODO: 实现获取单个条目逻辑
    return APIResponse(
        data=None,
        error="Item not found",
        meta={"requestId": request_id}
    )