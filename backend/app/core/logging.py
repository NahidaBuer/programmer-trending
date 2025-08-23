import logging
import sys
from typing import Optional, Dict, Any

from .config import get_settings


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色  
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        # 添加颜色
        color = self.COLORS.get(record.levelname, '')
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
    
    # 配置特定库的日志级别
    loggers_config = {
        "uvicorn": logging.INFO,           # 保持 uvicorn 主要信息
        "uvicorn.access": logging.WARNING,  # 隐藏访问日志
        "uvicorn.error": logging.INFO,     # 保持错误信息
        "sqlalchemy.engine": logging.INFO if settings.debug else logging.WARNING,  # 开发时显示SQL
        "sqlalchemy.pool": logging.WARNING,
        "httpx": logging.WARNING,
        "apscheduler": logging.INFO,       # 保持调度器日志
        "app": logging.INFO,               # 应用日志
    }
    
    for logger_name, logger_level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)
        # 确保使用相同的 handler
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False  # 防止重复输出


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name)


def get_uvicorn_log_config() -> dict[str, Any]:
    """获取 uvicorn 兼容的日志配置"""
    settings = get_settings()
    log_level = settings.log_level.upper()

    print(log_level) # WARNING
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "use_colors": False,  # uvicorn 会处理颜色
            },
            "colored": {
                "()": "app.core.logging.ColoredFormatter",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "colored",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # root logger
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": ["default"], 
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "INFO" if settings.debug else "WARNING",
                "handlers": ["default"],
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "level": "WARNING",
                "handlers": ["default"],
                "propagate": False,
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["default"],
                "propagate": False,
            },
            "apscheduler": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "app": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }