import math
from typing import Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse, PaginationMeta
from app.schemas.item import ItemResponse, ItemWithSummaryResponse, ItemWithSummaryListResponse
from app.models.item import Item
from app.models.summary import Summary

router = APIRouter()


@router.get("/", response_model=APIResponse[ItemWithSummaryListResponse])
async def get_items(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条目数"),
    source_id: Optional[str] = Query(None, description="数据源ID"),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[ItemWithSummaryListResponse]:
    """获取热榜条目列表"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        # 构建带摘要的联合查询 (LEFT JOIN)
        base_query = select(Item, Summary).select_from(
            Item.__table__.outerjoin(Summary.__table__, Item.id == Summary.item_id)
        ).order_by(Item.fetched_at.desc())
        
        # 计数查询（只计算Item）
        count_query = select(func.count(Item.id))
        
        # 按数据源过滤
        if source_id:
            base_query = base_query.where(Item.source_id == source_id)
            count_query = count_query.where(Item.source_id == source_id)
            
        # 获取总数
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 计算分页
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        offset = (page - 1) * page_size
        
        # 获取当前页数据
        items_query = base_query.limit(page_size).offset(offset)
        items_result = await db.execute(items_query)
        rows = items_result.all()
        
        # 转换为响应模型
        item_responses: list[ItemWithSummaryResponse] = []
        for item, summary in rows:
            response = ItemWithSummaryResponse(
                id=item.id,
                source_id=item.source_id,
                title=item.title,
                url=item.url,
                score=item.score,
                author=item.author,
                created_at=item.created_at,
                fetched_at=item.fetched_at,
                # 摘要信息（可能为None）
                summary_content=summary.content if summary else None,
                translated_title=summary.translated_title if summary else None,
                summary_status=summary.status if summary else None
            )
            item_responses.append(response)
        
        # 构建分页信息
        pagination = PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
        return APIResponse(
            data=ItemWithSummaryListResponse(items=item_responses, pagination=pagination),
            error=None,
            meta={"requestId": request_id}
        )
        
    except Exception as e:
        return APIResponse(
            data=ItemWithSummaryListResponse(items=[], pagination=PaginationMeta(
                page=page, page_size=page_size, total=0, total_pages=0,
                has_next=False, has_prev=False
            )),
            error=f"Failed to fetch items: {str(e)}",
            meta={"requestId": request_id}
        )


@router.get("/{item_id}", response_model=APIResponse[Optional[ItemResponse]])
async def get_item(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[Optional[ItemResponse]]:
    """获取单个条目详情"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        # 查询单个条目
        stmt = select(Item).where(Item.id == item_id)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()
        
        if not item:
            return APIResponse(
                data=None,
                error="Item not found",
                meta={"requestId": request_id}
            )
            
        # 转换为响应模型
        item_response = ItemResponse(
            id=item.id,
            source_id=item.source_id,
            title=item.title,
            url=item.url,
            score=item.score,
            author=item.author,
            created_at=item.created_at,
            fetched_at=item.fetched_at
        )
        
        return APIResponse(
            data=item_response,
            error=None,
            meta={"requestId": request_id}
        )
        
    except Exception as e:
        return APIResponse(
            data=None,
            error=f"Failed to fetch item: {str(e)}",
            meta={"requestId": request_id}
        )