"""
Google Gemini 流式聊天服务

使用官方 google-genai SDK 的流式 API 处理实时聊天对话
"""
import json
import time
from typing import AsyncGenerator, Optional, Dict, Any

from google import genai
from google.genai import types
from pydantic import BaseModel

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class ChatMessage(BaseModel):
    """聊天消息模型"""
    content: str
    context_url: Optional[str] = None


class RateLimiter:
    """全站速率限制器"""
    
    def __init__(self):
        # 全站限制：每10分钟5条消息
        # 开发阶段不考虑单IP限制，为全站共享
        self.global_limit = 5
        self.global_window = 600  # 10分钟
        self.global_requests: list[float] = []
    
    def check_global_limit(self) -> bool:
        """检查全站限制"""
        now = time.time()
        # 清理过期请求
        self.global_requests = [req_time for req_time in self.global_requests 
                               if now - req_time < self.global_window]
        
        if len(self.global_requests) >= self.global_limit:
            return False
            
        self.global_requests.append(now)
        return True
    
    def can_make_request(self) -> Dict[str, Any]:
        """检查是否可以发起请求"""
        if not self.check_global_limit():
            return {
                "allowed": False,
                "reason": "Global rate limit exceeded",
                "retry_after": self.global_window
            }
        
        return {"allowed": True}


class ChatService:
    """流式聊天服务（基于 Google Gen AI SDK）"""
    
    def __init__(self):
        self.settings = get_settings()
        self.rate_limiter = RateLimiter()
    
    def _build_chat_config(self, context_url: Optional[str] = None) -> types.GenerateContentConfig:
        """构建聊天配置"""
        config = types.GenerateContentConfig(
            temperature=0.7,  # 对话更灵活一些
            top_p=0.95,
            top_k=40,
        )
        
        # 如果有上下文URL，添加URL上下文工具
        if context_url:
            config.tools = [{"url_context": {}}]
        
        return config
    
    def _build_chat_contents(self, message: ChatMessage) -> str:
        """构建聊天内容"""
        if message.context_url:
            return f"基于以下页面内容回答问题：{message.context_url}\n\n问题：{message.content}"
        
        return message.content
    
    async def stream_chat_anonymous(
        self, 
        message: ChatMessage, 
    ) -> AsyncGenerator[str, None]:
        """匿名用户流式聊天（使用服务器API key + 限流）"""
        
        # 检查速率限制
        rate_check = self.rate_limiter.can_make_request()
        if not rate_check["allowed"]:
            yield f'data: {json.dumps({"error": rate_check["reason"], "retry_after": rate_check["retry_after"]})}\n\n'
            return
        
        # 使用服务器API key
        api_key = self.settings.google_api_key
        if not api_key:
            yield f'data: {json.dumps({"error": "服务器配置错误"})}\n\n'
            return
        
        async for chunk in self._stream_gemini_response_sdk(message, api_key):
            yield chunk
    
    async def stream_chat_with_user_key(
        self, 
        message: ChatMessage, 
        user_api_key: str
    ) -> AsyncGenerator[str, None]:
        """用户自己API key的流式聊天（无限流）"""
        async for chunk in self._stream_gemini_response_sdk(message, user_api_key):
            yield chunk
    
    async def _stream_gemini_response_sdk(
        self, 
        message: ChatMessage, 
        api_key: str
    ) -> AsyncGenerator[str, None]:
        """使用 Google Gen AI SDK 的核心流式响应处理"""
        
        try:
            # 创建客户端
            client = genai.Client(api_key=api_key)
            
            # 构建请求参数
            contents = self._build_chat_contents(message)
            config = self._build_chat_config(message.context_url)
            model = self.settings.gemini_model or "gemini-2.5-flash"
            
            logger.info(f"Starting streaming chat with model: {model}")
            logger.info(f"Message content: {message.content[:100]}...")
            
            # 使用 SDK 的异步流式方法
            async for chunk in await client.aio.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config
            ):
                if hasattr(chunk, 'text') and chunk.text:
                    text_content = chunk.text
                    logger.debug(f"Received chunk: {text_content[:50]}...")
                    yield f'data: {json.dumps({"text": text_content})}\n\n'
            
            # 流结束标记
            logger.info("Stream completed successfully")
            yield f'data: {json.dumps({"done": True})}\n\n'
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error in SDK streaming: {error_str}")
            
            # 检查是否是速率限制错误
            if "429" in error_str or "rate limit" in error_str.lower() or "quota" in error_str.lower():
                yield f'data: {json.dumps({"error": "API 速率限制，请稍后再试", "code": "RATE_LIMIT"})}\n\n'
            elif "403" in error_str or "forbidden" in error_str.lower():
                yield f'data: {json.dumps({"error": "API 密钥无效或权限不足", "code": "AUTH_ERROR"})}\n\n'
            elif "400" in error_str or "bad request" in error_str.lower():
                yield f'data: {json.dumps({"error": "请求格式错误", "code": "BAD_REQUEST"})}\n\n'
            else:
                yield f'data: {json.dumps({"error": f"服务器错误: {error_str}", "code": "SERVER_ERROR"})}\n\n'


# 全局实例
chat_service = ChatService()