from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from .config import get_settings

settings = get_settings()

# 根据数据库 URL 选择不同的引擎配置
if settings.database_url.startswith("sqlite"):
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        poolclass=NullPool,
    )
elif settings.database_url.startswith("postgresql"):
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
    )
else:
    raise ValueError(f"Unsupported database URL: {settings.database_url}")

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)

# 创建基础模型类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖函数"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """初始化数据库连接 (表结构由 Alembic 管理)"""
    # 注意: 数据库表结构应该通过 Alembic 迁移来管理
    # 不再使用 Base.metadata.create_all() 避免与 Alembic 冲突
    
    # 可以在这里添加数据库连接测试或其他初始化逻辑
    async with engine.begin() as conn:
        # 测试数据库连接
        from sqlalchemy import text
        await conn.execute(text("SELECT 1"))
        
    # 提示用户如果遇到表不存在的错误，需要运行 Alembic 迁移
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Database initialization completed. Use 'alembic upgrade head' to create/update tables.")


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()