from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条目数")
    total: int = Field(..., description="总条目数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class APIResponse(BaseModel, Generic[T]):
    data: Optional[T] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    meta: dict[str, Any] = Field(
        default_factory=dict, description="元数据，包含 requestId 等"
    )
