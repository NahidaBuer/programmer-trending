from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("sources.id"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    score = Column(Integer)
    author = Column(String)
    # 使用 func.now() 让数据库生成当前时间，而不是在应用层
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    fetched_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    source = relationship("Source", back_populates="items")
    summary = relationship("Summary", back_populates="item", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("source_id", "url", name="uix_source_url"),
    )