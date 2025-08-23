from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .source import Source
    from .summary import Summary


class Item(Base):
    __tablename__ = "items"

    # 主键和外键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[str] = mapped_column(String, ForeignKey("sources.id"))
    external_id: Mapped[str] = mapped_column(String)  # 外部系统ID (如HN的item id)
    
    # 基本信息
    title: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    score: Mapped[Optional[int]] = mapped_column(Integer)  # 分数(对于 Hacker News, 其他平台采用另外字段映射)
    author: Mapped[Optional[str]] = mapped_column(String)
    comments_count: Mapped[Optional[int]] = mapped_column(Integer)  # 评论数
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)  # 标签列表
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # 原始创建时间 (来自外部系统)
    fetched_at: Mapped[datetime] = mapped_column(  # 抓取时间 (我们的系统时间)
        DateTime(timezone=True), 
        default=func.now(), 
        onupdate=func.now()
    )

    # 关系（使用 TYPE_CHECKING 避免循环导入）
    source: Mapped["Source"] = relationship("Source", back_populates="items")
    summary: Mapped[Optional["Summary"]] = relationship(
        "Summary", 
        back_populates="item", 
        uselist=False, 
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        # 使用 source_id + external_id 作为唯一约束，而不是 URL
        UniqueConstraint("source_id", "external_id", name="uix_source_external_id"),
    )