from datetime import datetime
from pydantic import BaseModel, Field


class SourceBase(BaseModel):
    id: str = Field(..., description="数据源标识")
    name: str = Field(..., description="数据源名称")
    url: str = Field(..., description="数据源URL")
    enabled: bool = Field(True, description="是否启用")


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    enabled: bool | None = None


class SourceResponse(SourceBase):
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True