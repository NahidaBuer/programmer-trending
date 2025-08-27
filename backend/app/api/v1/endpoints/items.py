import math
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse, PaginationMeta
from app.schemas.item import (
    ItemResponse,
    ItemWithSummaryResponse,
    ItemWithSummaryListResponse,
)
from app.models.item import Item
from app.models.summary import Summary, SummaryStatus

router = APIRouter()


@router.get("/", response_model=APIResponse[ItemWithSummaryListResponse])
async def get_items(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条目数"),
    source_id: Optional[str] = Query(None, description="数据源ID"),
    days: Optional[int] = Query(
        None, ge=1, description="显示最近N天的新闻，不传则显示全部"
    ),
    has_summary: Optional[bool] = Query(
        None, description="是否筛选摘要：true=仅有摘要，false=仅无摘要，不传=全部"
    ),
    sort_by: Literal["score", "time"] = Query(
        "score", description="排序方式：score=按点赞数，time=按时间"
    ),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ItemWithSummaryListResponse]:
    """获取热榜条目列表"""
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # 构建带摘要的联合查询 (LEFT JOIN)
        base_query = select(Item, Summary).select_from(
            Item.__table__.outerjoin(Summary.__table__, Item.id == Summary.item_id)
        )

        # 根据排序参数设置排序规则
        if sort_by == "score":
            # 按点赞数排序（降序），点赞数相同时按时间排序
            base_query = base_query.order_by(Item.score.desc(), Item.created_at.desc())
        else:  # sort_by == "time"
            # 按时间排序（降序）
            base_query = base_query.order_by(Item.created_at.desc())

        # 计数查询（只计算Item）
        count_query = select(func.count(Item.id))

        # 按数据源过滤
        if source_id:
            base_query = base_query.where(Item.source_id == source_id)
            count_query = count_query.where(Item.source_id == source_id)

        # 按时间过滤（最近N天）
        if days:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            base_query = base_query.where(Item.created_at >= cutoff_date)
            count_query = count_query.where(Item.created_at >= cutoff_date)

        # 按摘要状态过滤
        if has_summary is not None:
            if has_summary:
                # 仅显示有摘要的（摘要存在且状态为完成）
                base_query = base_query.where(Summary.id.isnot(None))
                base_query = base_query.where(Summary.status == SummaryStatus.COMPLETED)
                count_query = count_query.select_from(
                    Item.__table__.join(Summary.__table__, Item.id == Summary.item_id)
                ).where(Summary.status == SummaryStatus.COMPLETED)
            else:
                # 仅显示无摘要的（摘要不存在或状态非完成）
                base_query = base_query.where(
                    (Summary.id.is_(None)) | (Summary.status != SummaryStatus.COMPLETED)
                )
                count_query = count_query.select_from(
                    Item.__table__.outerjoin(
                        Summary.__table__, Item.id == Summary.item_id
                    )
                ).where(
                    (Summary.id.is_(None)) | (Summary.status != SummaryStatus.COMPLETED)
                )

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
                summary_status=summary.status if summary else None,
            )
            item_responses.append(response)

        # 构建分页信息
        pagination = PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

        return APIResponse(
            data=ItemWithSummaryListResponse(
                items=item_responses, pagination=pagination
            ),
            error=None,
            meta={"requestId": request_id},
        )

    except Exception as e:
        return APIResponse(
            data=ItemWithSummaryListResponse(
                items=[],
                pagination=PaginationMeta(
                    page=page,
                    page_size=page_size,
                    total=0,
                    total_pages=0,
                    has_next=False,
                    has_prev=False,
                ),
            ),
            error=f"Failed to fetch items: {str(e)}",
            meta={"requestId": request_id},
        )


@router.get("/{item_id}", response_model=APIResponse[Optional[ItemResponse]])
async def get_item(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
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
                data=None, error="Item not found", meta={"requestId": request_id}
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
            fetched_at=item.fetched_at,
        )

        return APIResponse(
            data=item_response, error=None, meta={"requestId": request_id}
        )

    except Exception as e:
        return APIResponse(
            data=None,
            error=f"Failed to fetch item: {str(e)}",
            meta={"requestId": request_id},
        )
