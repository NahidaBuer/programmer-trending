"""
Google Gemini AI 服务

使用官方 google-genai SDK 实现原生异步 AI 服务
"""
import logging
import textwrap
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from enum import Enum

from google import genai
from google.genai import types

from ..core.config import get_settings
from ..models.item import Item

logger = logging.getLogger(__name__)


class URLRetrievalStatus(str, Enum):
    """URL 检索状态枚举"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE" 
    UNKNOWN = "UNKNOWN"


class GeminiAIService:
    """Google Gemini AI 服务（使用官方异步 SDK）"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[genai.Client] = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        if not self.settings.google_api_key:
            raise ValueError("Google API key not configured")
            
        # 初始化客户端
        self.client = genai.Client(api_key=self.settings.google_api_key)
        return self
        
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """异步上下文管理器出口"""
        self.client = None
            
    async def generate_summary(self, item: Item) -> Tuple[bool, Dict[str, Any]]:
        """
        为条目生成摘要
        
        Args:
            item: 需要生成摘要的条目
            
        Returns:
            (成功标志, 结果数据)
        """
        if not self.client:
            raise RuntimeError("Service not initialized. Use 'async with' context manager.")
            
        try:
            # 构建提示词
            prompt = self._build_summary_prompt(item)
            start_time = datetime.now()
            
            # 使用原生异步 API 调用 Gemini
            response = await self.client.aio.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[{"url_context": {}}],  # URL 上下文工具
                    max_output_tokens=self.settings.ai_summary_max_length * 2,  # 预留空间
                    temperature=0.3  # 保持一致性
                )
            )
            
            generation_duration = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # 处理响应
            return await self._process_gemini_response(response, generation_duration)
            
        except Exception as e:
            logger.error(f"Error generating summary for item {item.id}: {e}")
            return False, {"error": str(e)}
    
    def _build_summary_prompt(self, item: Item) -> str:
        """构建摘要生成的提示词"""
        max_length = self.settings.ai_summary_max_length
        
        # 基础提示词
        base_prompt = f"""请总结这个页面的内容，要求：
        1. 用中文回复
        2. 不超过{max_length}字
        3. 重点突出技术要点和核心内容
        4. 保持客观和准确

        页面链接：{item.url}"""
            
        return textwrap.dedent(base_prompt)
    
    async def _process_gemini_response(
        self, 
        response: Any, 
        generation_duration: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """处理 Gemini API 响应"""
        try:
            # 检查是否有候选结果
            if not response.candidates:
                return False, {
                    "error": "No candidates in response",
                    "generation_duration_ms": generation_duration
                }
                
            candidate = response.candidates[0]
            
            # 提取文本内容
            if not hasattr(response, 'text') or not response.text:
                return False, {
                    "error": "No text content in response",
                    "generation_duration_ms": generation_duration
                }
                
            summary_content = response.text.strip()
            
            if not summary_content:
                return False, {
                    "error": "Empty summary content",
                    "generation_duration_ms": generation_duration
                }
            
            # 提取 URL 检索状态（从候选结果的元数据中）
            url_retrieval_status = URLRetrievalStatus.UNKNOWN
            
            # 检查是否有 URL 上下文元数据
            if hasattr(candidate, 'grounding_metadata'):
                grounding_metadata = candidate.grounding_metadata
                if grounding_metadata and hasattr(grounding_metadata, 'grounding_chunks'):
                    chunks = grounding_metadata.grounding_chunks
                    if chunks and len(chunks) > 0:
                        # 如果有接地信息块，表示 URL 检索成功
                        url_retrieval_status = URLRetrievalStatus.SUCCESS
                    else:
                        url_retrieval_status = URLRetrievalStatus.FAILURE
            
            return True, {
                "content": summary_content,
                "generation_duration_ms": generation_duration,
                "url_retrieval_status": url_retrieval_status.value,
                "response_json": self._response_to_dict(response)
            }
            
        except Exception as e:
            logger.error(f"Error processing Gemini response: {e}")
            return False, {
                "error": f"Response processing error: {str(e)}",
                "generation_duration_ms": generation_duration
            }
    
    async def generate_chat_response(
        self, 
        message: str, 
        context_url: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        生成对话响应
        
        Args:
            message: 用户消息
            context_url: 可选的上下文URL
            
        Returns:
            (成功标志, 结果数据)
        """
        if not self.client:
            raise RuntimeError("Service not initialized. Use 'async with' context manager.")
            
        try:
            # 构建提示词
            prompt = message
            if context_url:
                prompt = f"基于以下页面内容回答问题：{context_url}\n\n问题：{message}"
                
            # 构建配置
            config = types.GenerateContentConfig(
                temperature=0.7,  # 对话更灵活一些
                max_output_tokens=1000  # 对话可以稍长
            )
            
            # 如果有上下文URL，添加URL上下文工具
            if context_url:
                config.tools = [{"url_context": {}}]
                
            # 使用原生异步 API
            response = await self.client.aio.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=config
            )
            
            # 提取回复内容
            if not hasattr(response, 'text') or not response.text:
                return False, {"error": "No text content in response"}
                
            reply_content = response.text.strip()
            
            return True, {
                "reply": reply_content,
                "response_json": self._response_to_dict(response)
            }
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return False, {"error": str(e)}
    
    def _response_to_dict(self, response: Any) -> Dict[str, Any]:
        """将响应对象转换为字典（用于JSON存储）"""
        try:
            # 简化的响应信息提取
            result = {
                "model_used": self.settings.gemini_model,
                "has_candidates": bool(response.candidates) if hasattr(response, 'candidates') else False,
                "text_length": len(response.text) if hasattr(response, 'text') and response.text else 0
            }
            
            # 添加使用元数据（如果存在）
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                result["usage"] = {
                    "prompt_token_count": getattr(usage, 'prompt_token_count', 0),
                    "candidates_token_count": getattr(usage, 'candidates_token_count', 0),
                    "total_token_count": getattr(usage, 'total_token_count', 0)
                }
                
            return result
            
        except Exception as e:
            logger.warning(f"Failed to convert response to dict: {e}")
            return {"error": "Failed to serialize response"}


# 全局 AI 服务实例
ai_service = GeminiAIService()