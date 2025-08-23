from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .item import Item


class Source(Base):
    __tablename__ = "sources"

    # 基本信息
    id: Mapped[str] = mapped_column(String, primary_key=True)  # 如 "hackernews"
    name: Mapped[str] = mapped_column(String)  # 如 "Hacker News"
    url: Mapped[str] = mapped_column(String)   # 数据源URL
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否启用
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    items: Mapped[List["Item"]] = relationship("Item", back_populates="source", cascade="all, delete-orphan")