from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("sources.id"), nullable=False)
    external_id = Column(String, nullable=False)  # 外部系统ID (如HN的item id)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    score = Column(Integer)             # 分数(对于 Hacker News, 其他平台采用另外字段映射)
    author = Column(String)
    comments_count = Column(Integer)    # 评论数
    tags = Column(JSON, default=list)   # 标签列表
    # 原始创建时间 (来自外部系统)
    created_at = Column(DateTime(timezone=True), nullable=False)
    # 抓取时间 (我们的系统时间)
    fetched_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # 关系
    source = relationship("Source", back_populates="items")
    summary = relationship("Summary", back_populates="item", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        # 使用 source_id + external_id 作为唯一约束，而不是 URL
        UniqueConstraint("source_id", "external_id", name="uix_source_external_id"),
    )