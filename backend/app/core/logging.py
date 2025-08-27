import logging
import sys
from typing import Optional

from .config import get_settings


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # ANSI 颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # 添加颜色
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname:<8}{self.RESET}"
        record.name = f"\033[94m{record.name}\033[0m"  # 蓝色
        return super().format(record)


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
) -> None:
    """设置日志配置"""
    settings = get_settings()

    # 日志级别
    log_level = level or settings.log_level.upper()

    # 日志格式
    # 2025-08-21 18:14:48,750 - uvicorn.error - INFO     - Waiting for application startup.
    log_format = format_string or (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 创建彩色 handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter(log_format))

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # 清除现有处理器
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    # 强制重新配置关键日志器，确保格式统一（特别是 uvicorn CLI 启动时）
    critical_loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "sqlalchemy",  # SQLAlchemy 根日志器
        "sqlalchemy.engine",  # SQL 执行日志
        "sqlalchemy.pool",  # 连接池日志
        "apscheduler.scheduler",
    ]

    for logger_name in critical_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()  # 强制清除所有现有处理器
        logger.addHandler(handler)
        # SQLAlchemy 根据配置文件设置不同级别，覆盖默认值
        if logger_name.startswith("sqlalchemy"):
            logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.propagate = False  # 防止重复输出


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name)
