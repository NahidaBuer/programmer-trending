from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse
from app.schemas.summary import SummaryResponse, SummaryCreate
from app.models.summary import Summary, SummaryStatus
from app.models.item import Item
from app.tasks.summary_generator import summary_generator
from app.tasks.scheduler import task_scheduler

router = APIRouter()


@router.get("/{item_id}", response_model=APIResponse[Optional[SummaryResponse]])
async def get_summary(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
) -> APIResponse[Optional[SummaryResponse]]:
    """获取指定文章的摘要"""
    request_id = getattr(request.state, "request_id", "unknown")

    # 查询摘要
    result = await db.execute(select(Summary).where(Summary.item_id == item_id))
    summary = result.scalar_one_or_none()

    data = None
    if summary:
        data = SummaryResponse(
            id=summary.id,
            item_id=summary.item_id,
            model=summary.model,
            lang=summary.lang,
            content=summary.content,
            translated_title=summary.translated_title,
            status=summary.status,
            retry_count=summary.retry_count,
            max_retries=summary.max_retries,
            created_at=summary.created_at,
            started_at=summary.started_at,
            completed_at=summary.completed_at,
            error_message=summary.error_message,
            generation_duration_ms=summary.generation_duration_ms,
            url_retrieval_status=summary.url_retrieval_status,
        )

    return APIResponse(data=data, error=None, meta={"requestId": request_id})


@router.post("/", response_model=APIResponse[SummaryResponse])
async def create_summary(
    request: Request, summary_data: SummaryCreate, db: AsyncSession = Depends(get_db)
) -> APIResponse[SummaryResponse]:
    """为指定文章创建摘要任务"""
    request_id = getattr(request.state, "request_id", "unknown")

    # 检查文章是否存在
    item_result = await db.execute(select(Item).where(Item.id == summary_data.item_id))
    item = item_result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # 检查是否已存在摘要
    existing_result = await db.execute(
        select(Summary).where(Summary.item_id == summary_data.item_id)
    )
    existing_summary = existing_result.scalar_one_or_none()
    if existing_summary:
        raise HTTPException(status_code=409, detail="Summary already exists")

    # 创建摘要任务
    summary = Summary(
        item_id=summary_data.item_id,
        model=summary_data.model,
        lang=summary_data.lang,
        status=summary_data.status,
        retry_count=0,
        max_retries=summary_data.max_retries,
    )

    db.add(summary)
    await db.commit()
    await db.refresh(summary)

    data = SummaryResponse(
        id=summary.id,
        item_id=summary.item_id,
        model=summary.model,
        lang=summary.lang,
        content=summary.content,
        translated_title=summary.translated_title,
        status=summary.status,
        retry_count=summary.retry_count,
        max_retries=summary.max_retries,
        created_at=summary.created_at,
        started_at=summary.started_at,
        completed_at=summary.completed_at,
        error_message=summary.error_message,
        generation_duration_ms=summary.generation_duration_ms,
        url_retrieval_status=summary.url_retrieval_status,
    )

    return APIResponse(data=data, error=None, meta={"requestId": request_id})


@router.get("/", response_model=APIResponse[List[SummaryResponse]])
async def list_summaries(
    request: Request,
    status: Optional[SummaryStatus] = Query(None, description="按状态筛选"),
    limit: int = Query(20, le=100, description="返回条目数量"),
    offset: int = Query(0, description="偏移量"),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[SummaryResponse]]:
    """获取摘要列表"""
    request_id = getattr(request.state, "request_id", "unknown")

    # 构建查询
    stmt = select(Summary).order_by(Summary.created_at.desc())

    if status:
        stmt = stmt.where(Summary.status == status)

    stmt = stmt.offset(offset).limit(limit)

    # 执行查询
    result = await db.execute(stmt)
    summaries = result.scalars().all()

    data = [
        SummaryResponse(
            id=summary.id,
            item_id=summary.item_id,
            model=summary.model,
            lang=summary.lang,
            content=summary.content,
            translated_title=summary.translated_title,
            status=summary.status,
            retry_count=summary.retry_count,
            max_retries=summary.max_retries,
            created_at=summary.created_at,
            started_at=summary.started_at,
            completed_at=summary.completed_at,
            error_message=summary.error_message,
            generation_duration_ms=summary.generation_duration_ms,
            url_retrieval_status=summary.url_retrieval_status,
        )
        for summary in summaries
    ]

    return APIResponse(data=data, error=None, meta={"requestId": request_id})


@router.post("/generate", response_model=APIResponse[Dict[str, Any]])
async def trigger_summary_generation(request: Request) -> APIResponse[Dict[str, Any]]:
    """手动触发摘要生成任务"""
    request_id = getattr(request.state, "request_id", "unknown")

    result = await task_scheduler.trigger_manual_summary_generation()

    return APIResponse(data=result, error=None, meta={"requestId": request_id})


@router.post("/batch-create", response_model=APIResponse[Dict[str, Any]])
async def batch_create_summary_tasks(
    request: Request,
    source_id: Optional[str] = Query(
        None, description="指定数据源ID，为空则处理所有数据源"
    ),
    model: str = Query("gemini-2.5-flash", description="使用的AI模型"),
    lang: str = Query("zh-CN", description="摘要语言"),
) -> APIResponse[Dict[str, Any]]:
    """为所有没有摘要的文章批量创建摘要任务"""
    request_id = getattr(request.state, "request_id", "unknown")

    result = await summary_generator.create_summary_tasks_for_missing_items(
        source_id=source_id, model=model, lang=lang
    )

    return APIResponse(data=result, error=None, meta={"requestId": request_id})


@router.post("/batch-create-and-generate", response_model=APIResponse[Dict[str, Any]])
async def batch_create_and_generate_summaries(
    request: Request,
    source_id: Optional[str] = Query(
        None, description="指定数据源ID，为空则处理所有数据源"
    ),
    model: str = Query("gemini-2.5-flash", description="使用的AI模型"),
    lang: str = Query("zh-CN", description="摘要语言"),
) -> APIResponse[Dict[str, Any]]:
    """批量创建摘要任务并立即开始生成"""
    request_id = getattr(request.state, "request_id", "unknown")

    # 先批量创建任务
    create_result = await summary_generator.create_summary_tasks_for_missing_items(
        source_id=source_id, model=model, lang=lang
    )

    # 如果创建了新任务，立即触发生成
    if create_result.get("created_count", 0) > 0:
        generate_result = await task_scheduler.trigger_manual_summary_generation()

        return APIResponse(
            data={
                "batch_create": create_result,
                "generation_triggered": generate_result,
            },
            error=None,
            meta={"requestId": request_id},
        )
    else:
        return APIResponse(
            data={
                "batch_create": create_result,
                "generation_triggered": {"message": "No new tasks to process"},
            },
            error=None,
            meta={"requestId": request_id},
        )
