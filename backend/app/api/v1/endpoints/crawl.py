from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse
from app.tasks.scheduler import task_scheduler

router = APIRouter()


@router.post("/trigger", response_model=APIResponse[Dict[str, Any]])
async def trigger_crawl(
    request: Request,
    source_id: Optional[str] = Query(
        None, description="指定数据源ID，为空则爬取所有源"
    ),
    limit: int = Query(30, description="爬取条目数量限制"),
    _: AsyncSession = Depends(get_db),
) -> APIResponse[Dict[str, Any]]:
    """手动触发爬取任务"""
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        result = await task_scheduler.trigger_manual_crawl(source_id, limit)

        if result["success"]:
            return APIResponse(data=result, error=None, meta={"requestId": request_id})
        else:
            return APIResponse(
                data=result,
                error=result.get("error", "Unknown error"),
                meta={"requestId": request_id},
            )

    except Exception as e:
        return APIResponse(
            data={"success": False, "error": str(e)},
            error=f"Failed to trigger crawl: {str(e)}",
            meta={"requestId": request_id},
        )


@router.get("/status", response_model=APIResponse[Dict[str, Any]])
async def get_crawl_status(
    request: Request, _: AsyncSession = Depends(get_db)
) -> APIResponse[Dict[str, Any]]:
    """获取爬取任务状态"""
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        status = task_scheduler.get_job_status()

        return APIResponse(data=status, error=None, meta={"requestId": request_id})

    except Exception as e:
        return APIResponse(
            data={"scheduler_running": False, "jobs": []},
            error=f"Failed to get crawl status: {str(e)}",
            meta={"requestId": request_id},
        )
