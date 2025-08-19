from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True)  # 如 "hackernews"
    name = Column(String, nullable=False)  # 如 "Hacker News"

    # 关联关系
    items = relationship("Item", back_populates="source", cascade="all, delete-orphan")