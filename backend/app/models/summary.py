from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
import enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Enum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .item import Item


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

    # 主键和外键
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), unique=True)
    
    # 基本信息
    model: Mapped[str] = mapped_column(String)  # AI 模型名称，如 "gemini-2.5-flash"
    lang: Mapped[str] = mapped_column(String, default="zh-CN")  # 语言
    content: Mapped[Optional[str]] = mapped_column(Text)  # 摘要内容（状态为COMPLETED时必填）
    translated_title: Mapped[Optional[str]] = mapped_column(String(500))  # 翻译后的标题（对应lang字段的语言）
    
    # 状态管理
    status: Mapped[SummaryStatus] = mapped_column(Enum(SummaryStatus), default=SummaryStatus.PENDING)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # 时间追踪  
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_type: Mapped[Optional[str]] = mapped_column(String)  # "NETWORK_ERROR", "CONTENT_ERROR", "API_ERROR"
    
    # Gemini 特有的元数据
    generation_duration_ms: Mapped[Optional[int]] = mapped_column(Integer)  # 生成耗时(毫秒)
    url_retrieval_status: Mapped[Optional[str]] = mapped_column(String)     # URL检索状态
    response_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)   # API原始响应内容
    
    # 关联关系
    item: Mapped["Item"] = relationship("Item", back_populates="summary")