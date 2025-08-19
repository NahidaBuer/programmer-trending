from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True)  # 如 "hackernews"
    name = Column(String, nullable=False)  # 如 "Hacker News"
    url = Column(String, nullable=False)   # 数据源URL
    enabled = Column(Boolean, default=True, nullable=False)  # 是否启用
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # 关联关系
    items = relationship("Item", back_populates="source", cascade="all, delete-orphan")