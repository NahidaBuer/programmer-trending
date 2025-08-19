from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse
from app.schemas.source import SourceResponse
from app.models.source import Source

router = APIRouter()


@router.get("/", response_model=APIResponse[List[SourceResponse]])
async def get_sources(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[List[SourceResponse]]:
    """获取数据源列表"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        # 查询所有数据源
        stmt = select(Source).order_by(Source.name)
        result = await db.execute(stmt)
        sources = result.scalars().all()
        
        # 转换为响应模型
        source_responses = [
            SourceResponse(
                id=source.id,
                name=source.name,
                url=source.url,
                enabled=source.enabled,
                created_at=source.created_at,
                updated_at=source.updated_at
            )
            for source in sources
        ]
        
        return APIResponse(
            data=source_responses,
            error=None,
            meta={"requestId": request_id}
        )
        
    except Exception as e:
        return APIResponse(
            data=[],
            error=f"Failed to fetch sources: {str(e)}",
            meta={"requestId": request_id}
        )