from fastapi import APIRouter

from .endpoints import sources, items, summaries, crawl, chat

api_router = APIRouter()

api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
api_router.include_router(crawl.router, prefix="/crawl", tags=["crawl"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
