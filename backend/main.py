import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Any, Dict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.schemas.common import APIResponse
from app.tasks.scheduler import task_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    
    # 启动任务调度器
    await task_scheduler.start()
    
    yield
    
    # 关闭时清理资源
    await task_scheduler.stop()
    await close_db()


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # 前端开发服务器
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.middleware("http")
    async def add_request_id_middleware(request: Request, call_next: Callable[[Request], Any]) -> Response:
        """为每个请求添加唯一ID"""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理"""
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=500,
            content=APIResponse(
                data=None,
                error=f"Internal server error: {str(exc)}",
                meta={"requestId": request_id}
            ).model_dump()
        )
    
    # 健康检查接口
    @app.get("/health")
    async def health_check(request: Request) -> APIResponse[Dict[str, str]]:
        request_id = getattr(request.state, "request_id", "unknown")
        return APIResponse(
            data={"status": "healthy", "service": settings.app_name},
            error=None,
            meta={"requestId": request_id}
        )
    
    # 注册 API 路由
    from app.api.v1 import api_router
    app.include_router(api_router, prefix="/api/v1")
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
