from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class SummaryStatus(str, enum.Enum):
    """摘要生成状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    PERMANENTLY_FAILED = "permanently_failed"
    SKIPPED = "skipped"


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), unique=True, nullable=False)
    
    # 基本信息
    model = Column(String, nullable=False)  # AI 模型名称，如 "gemini-2.5-flash"
    lang = Column(String, nullable=False, default="zh-CN")  # 语言
    content = Column(Text)  # 摘要内容（状态为COMPLETED时必填）
    translated_title = Column(String(500))  # 翻译后的标题（对应lang字段的语言）
    
    # 状态管理
    status = Column(Enum(SummaryStatus), default=SummaryStatus.PENDING, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # 时间追踪  
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    last_retry_at = Column(DateTime(timezone=True))
    
    # 错误信息
    error_message = Column(Text)
    error_type = Column(String)  # "NETWORK_ERROR", "CONTENT_ERROR", "API_ERROR"
    
    # Gemini 特有的元数据
    generation_duration_ms = Column(Integer)  # 生成耗时(毫秒)
    url_retrieval_status = Column(String)     # URL检索状态
    response_json = Column(JSON)              # API原始响应内容
    
    # 关联关系
    item = relationship("Item", back_populates="summary")