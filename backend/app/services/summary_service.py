"""
Google Gemini AI 服务

使用官方 google-genai SDK 实现原生异步 AI 服务
"""

import asyncio
import json
import textwrap
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from collections import deque

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models.item import Item

logger = get_logger(__name__)


class SummaryResult(BaseModel):
    """AI 摘要生成结果的 Pydantic 模型"""

    translated_title: Optional[str] = Field(
        None, description="翻译后的标题，如果翻译失败则为null"
    )
    summary: Optional[str] = Field(None, description="文章摘要，如果生成失败则为null")


class URLRetrievalStatus(str, Enum):
    """URL 检索状态枚举"""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"


class GeminiSummaryService:
    """Google Gemini AI 服务（使用官方异步 SDK）"""

    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[genai.Client] = None

        # 速率限制状态
        self.request_times_minute: deque[datetime] = deque()  # 每分钟请求记录
        self.request_times_day: deque[datetime] = deque()  # 每天请求记录
        self._rate_limit_lock = asyncio.Lock()  # 防止并发检查冲突

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

    async def _check_and_record_rate_limit(self) -> bool:
        """检查速率限制并记录请求（原子操作）"""
        if not self.settings.ai_enable_rate_limiting:
            return True

        async with self._rate_limit_lock:
            now = datetime.now()

            # 清理过期的请求记录
            self._cleanup_expired_requests(now)

            # 检查每分钟限制
            if len(self.request_times_minute) >= self.settings.ai_rate_limit_per_minute:
                logger.warning(
                    f"达到每分钟请求限制 ({self.settings.ai_rate_limit_per_minute})"
                )
                return False

            # 检查每天限制
            if len(self.request_times_day) >= self.settings.ai_rate_limit_per_day:
                logger.warning(
                    f"达到每天请求限制 ({self.settings.ai_rate_limit_per_day})"
                )
                return False

            # 通过检查，立即记录本次请求
            self.request_times_minute.append(now)
            self.request_times_day.append(now)

            return True

    def _cleanup_expired_requests(self, now: datetime) -> None:
        """清理滑动窗口中过期的请求记录"""
        # 清理1分钟前的记录
        minute_ago = now - timedelta(minutes=1)
        while self.request_times_minute and self.request_times_minute[0] <= minute_ago:
            self.request_times_minute.popleft()

        # 清理1天前的记录
        day_ago = now - timedelta(days=1)
        while self.request_times_day and self.request_times_day[0] <= day_ago:
            self.request_times_day.popleft()

    async def _wait_for_rate_limit_reset(self) -> None:
        """等待速率限制重置"""
        logger.info(
            f"等待速率限制重置，延迟 {self.settings.ai_rate_limit_retry_delay} 秒"
        )
        await asyncio.sleep(self.settings.ai_rate_limit_retry_delay)

    async def generate_summary(self, item: Item) -> Tuple[bool, Dict[str, Any]]:
        """
        为条目生成摘要（带速率限制和重试机制）

        Args:
            item: 需要生成摘要的条目

        Returns:
            (成功标志, 结果数据)
        """
        if not self.client:
            raise RuntimeError(
                "Service not initialized. Use 'async with' context manager."
            )

        max_retries = 3  # 429错误最大重试次数
        retry_count = 0

        while retry_count <= max_retries:
            try:
                # 检查速率限制并记录请求（原子操作）
                if not await self._check_and_record_rate_limit():
                    # 速率限制达到，等待后重试
                    logger.warning(
                        f"Speed rate limit reached (retry {retry_count + 1}/{max_retries + 1})"
                    )
                    retry_count += 1

                    if retry_count <= max_retries:
                        await self._wait_for_rate_limit_reset()
                        continue
                    else:
                        return False, {"error": "Rate limit exceeded after max retries"}

                # 构建提示词
                prompt = self._build_summary_prompt(item)
                start_time = datetime.now()

                # 使用原生异步 API 调用 Gemini（手动JSON解析）
                response = await self.client.aio.models.generate_content(
                    model=self.settings.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[{"url_context": {}}],  # URL 上下文工具
                        max_output_tokens=self.settings.ai_summary_max_length
                        * 10,  # 预留空间
                        temperature=0.3,  # 保持一致性
                        thinking_config=types.ThinkingConfig(
                            thinking_budget=0, include_thoughts=False
                        ),
                    ),
                )

                logger.info(f"Gemini response: {response}")

                generation_duration = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )

                # 处理响应
                return await self._process_gemini_response(
                    response, generation_duration
                )

            except Exception as e:
                error_str = str(e)

                # 检查是否是429错误（速率限制）
                if (
                    "429" in error_str
                    or "rate limit" in error_str.lower()
                    or "quota" in error_str.lower()
                ):
                    logger.warning(
                        f"遇到速率限制错误 (重试 {retry_count + 1}/{max_retries + 1}): {error_str}"
                    )
                    retry_count += 1

                    if retry_count <= max_retries:
                        # 等待后重试
                        await self._wait_for_rate_limit_reset()
                        continue
                    else:
                        logger.error(f"达到最大重试次数，放弃生成摘要: {error_str}")
                        return False, {
                            "error": f"Rate limit exceeded after {max_retries} retries: {error_str}"
                        }
                else:
                    # 其他错误不重试
                    logger.error(
                        f"Error generating summary for item {item.id}: {error_str}"
                    )
                    return False, {"error": error_str}

        # 不应该到达这里
        return False, {"error": "Unexpected error in retry loop"}

    def _build_summary_prompt(self, item: Item) -> str:
        """构建摘要生成的提示词"""
        max_length = self.settings.ai_summary_max_length

        # 基础提示词
        base_prompt = f"""Please analyze the content of the page and generate a summary in CHINESE. The summary should be concise and highlight the key technical points and core content. The summary should be no more than {max_length} words. The summary should be objective and accurate. The summary should be returned in JSON format: {{"translated_title": "Chinese title", "summary": "Chinese summary"}}. If you cannot generate a summary, return null for summary, but you must return a valid JSON text with translated_title. YOU MUST RETURN A SINGLE JSON TEXT IN A SINGLE PART. DO NOT RETURN ANY OTHER TEXT, DO NOT RETURN MARKDOWN EITHER.

        Original title: {item.title}
        Page link: {item.url}"""

        return textwrap.dedent(base_prompt)

    async def _process_gemini_response(
        self, response: Any, generation_duration: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """处理 Gemini API 响应"""
        try:
            # 检查是否有候选结果
            if not response.candidates:
                return False, {
                    "error": "No candidates in response",
                    "generation_duration_ms": generation_duration,
                }

            candidate = response.candidates[0]

            # 提取文本内容并手动解析JSON
            if not hasattr(response, "text") or not response.text:
                return False, {
                    "error": "No text content in response",
                    "generation_duration_ms": generation_duration,
                }

            raw_content = response.text.strip()

            if not raw_content:
                return False, {
                    "error": "Empty response content",
                    "generation_duration_ms": generation_duration,
                }

            # 尝试解析JSON响应
            try:
                # 清理可能的markdown格式
                json_content = raw_content
                if raw_content.startswith("```json"):
                    # 移除markdown代码块标记
                    lines = raw_content.split("\n")
                    json_lines = []
                    in_json = False
                    for line in lines:
                        if line.strip() == "```json":
                            in_json = True
                            continue
                        elif line.strip() == "```":
                            break
                        elif in_json:
                            json_lines.append(line)
                    json_content = "\n".join(json_lines)

                # 解析JSON
                parsed_data = json.loads(json_content)

                # 验证必需的字段
                if not isinstance(parsed_data, dict):
                    raise ValueError("Response is not a JSON object")

                if (
                    "translated_title" not in parsed_data
                    or "summary" not in parsed_data
                ):
                    raise ValueError(
                        "Missing required fields: translated_title or summary"
                    )

                translated_title = parsed_data.get("translated_title", "")
                summary_content = parsed_data.get("summary", "")

                # 处理null值
                if translated_title is None:
                    translated_title = ""
                if summary_content is None:
                    summary_content = ""

                # 至少要有摘要内容才算成功
                if not summary_content.strip():
                    logger.warning("AI returned empty summary content")
                    summary_content = ""  # 允许空摘要，但记录警告

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"Failed to parse JSON response, using raw content as summary: {e}"
                )
                # 回退到原始内容作为摘要，translated_title为空
                translated_title = ""
                summary_content = raw_content

            # 提取 URL 检索状态（从候选结果的元数据中）
            url_retrieval_status = URLRetrievalStatus.UNKNOWN

            # 检查是否有 URL 上下文元数据
            if hasattr(candidate, "grounding_metadata"):
                grounding_metadata = candidate.grounding_metadata
                if grounding_metadata and hasattr(
                    grounding_metadata, "grounding_chunks"
                ):
                    chunks = grounding_metadata.grounding_chunks
                    if chunks and len(chunks) > 0:
                        # 如果有接地信息块，表示 URL 检索成功
                        url_retrieval_status = URLRetrievalStatus.SUCCESS
                    else:
                        url_retrieval_status = URLRetrievalStatus.FAILURE

            return True, {
                "content": summary_content,
                "translated_title": translated_title,
                "generation_duration_ms": generation_duration,
                "url_retrieval_status": url_retrieval_status.value,
                "response_json": self._response_to_dict(response),
            }

        except Exception as e:
            logger.error(f"Error processing Gemini response: {e}")
            return False, {
                "error": f"Response processing error: {str(e)}",
                "generation_duration_ms": generation_duration,
            }

    async def generate_chat_response(
        self, message: str, context_url: Optional[str] = None
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
            raise RuntimeError(
                "Service not initialized. Use 'async with' context manager."
            )

        try:
            # 构建提示词
            prompt = message
            if context_url:
                prompt = f"基于以下页面内容回答问题：{context_url}\n\n问题：{message}"

            # 构建配置
            config = types.GenerateContentConfig(
                temperature=0.7,  # 对话更灵活一些
                max_output_tokens=1000,  # 对话可以稍长
            )

            # 如果有上下文URL，添加URL上下文工具
            if context_url:
                config.tools = [{"url_context": {}}]

            # 使用原生异步 API
            response = await self.client.aio.models.generate_content(
                model=self.settings.gemini_model, contents=prompt, config=config
            )

            # 提取回复内容
            if not hasattr(response, "text") or not response.text:
                return False, {"error": "No text content in response"}

            reply_content = response.text.strip()

            return True, {
                "reply": reply_content,
                "response_json": self._response_to_dict(response),
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
                "has_candidates": bool(response.candidates)
                if hasattr(response, "candidates")
                else False,
                "text_length": len(response.text)
                if hasattr(response, "text") and response.text
                else 0,
            }

            # 添加使用元数据（如果存在）
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = response.usage_metadata
                result["usage"] = {
                    "prompt_token_count": getattr(usage, "prompt_token_count", 0),
                    "candidates_token_count": getattr(
                        usage, "candidates_token_count", 0
                    ),
                    "total_token_count": getattr(usage, "total_token_count", 0),
                }

            return result

        except Exception as e:
            logger.warning(f"Failed to convert response to dict: {e}")
            return {"error": "Failed to serialize response"}


# 全局 AI 服务实例
summary_service = GeminiSummaryService()
