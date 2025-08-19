from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), unique=True, nullable=False)
    model = Column(String, nullable=False)  # AI 模型名称，如 "deepseek-chat"
    lang = Column(String, nullable=False, default="zh-CN")  # 语言
    content = Column(Text, nullable=False)  # 摘要内容
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    # 关联关系
    item = relationship("Item", back_populates="summary")