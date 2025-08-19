from pydantic import BaseModel, Field


class SourceBase(BaseModel):
    id: str = Field(..., description="数据源标识")
    name: str = Field(..., description="数据源名称")


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    class Config:
        from_attributes = True