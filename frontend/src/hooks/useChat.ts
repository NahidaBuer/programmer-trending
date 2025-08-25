import { useState, useCallback, useRef } from "react";
import { API_SERVER_URL } from "../api/client";
import type { Message } from "../components/MessageBubble";
import type { ChatRequest, ChatMessage, ChatStreamChunk } from "../types/api";

interface ChatOptions {
  apiKey?: string | null;
}

interface ChatHookReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string, contextUrl?: string) => Promise<void>;
  clearMessages: () => void;
}

export function useChat(options: ChatOptions = {}): ChatHookReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (isLoading) return;

      // 取消之前的请求
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      setIsLoading(true);
      setError(null);

      // 添加用户消息
      const userMessage: Message = {
        id: Date.now().toString(),
        content,
        isUser: true,
        timestamp: new Date(),
      };

      // 创建 AI 回复消息（初始为空，流式更新）
      const aiMessageId = (Date.now() + 1).toString();
      const aiMessage: Message = {
        id: aiMessageId,
        content: "",
        isUser: false,
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, userMessage, aiMessage]);

      try {
        // 创建新的 AbortController
        const controller = new AbortController();
        abortControllerRef.current = controller;

        // 构建请求
        const endpoint = options.apiKey
          ? "/api/v1/chat/stream/user-key"
          : "/api/v1/chat/stream";

        const headers: Record<string, string> = {
          "Content-Type": "application/json",
        };

        if (options.apiKey) {
          headers["X-API-Key"] = options.apiKey;
        }

        // 构建消息历史
        const chatMessages: ChatMessage[] = [];

        // 添加历史消息
        for (const msg of messages) {
          chatMessages.push({
            role: msg.isUser ? "user" : "model",
            content: msg.content,
          });
        }

        // 添加当前用户消息
        chatMessages.push({
          role: "user",
          content,
        });

        const requestBody: ChatRequest = {
          messages: chatMessages,
        };

        // 发起 SSE 请求
        const response = await fetch(`${API_SERVER_URL}${endpoint}`, {
          method: "POST",
          headers,
          body: JSON.stringify(requestBody),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (!response.body) {
          throw new Error("Response body is null");
        }

        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            // 解码数据
            buffer += decoder.decode(value, { stream: true });

            // 处理可能包含多个事件的缓冲区
            const lines = buffer.split("\n");
            buffer = lines.pop() || ""; // 保留最后一个可能不完整的行

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                const data = line.slice(6); // 去掉 'data: '

                try {
                  const parsed: ChatStreamChunk = JSON.parse(data);

                  if (parsed.error) {
                    // 处理错误
                    setError(parsed.error);
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMessageId
                          ? {
                              ...msg,
                              content: `错误: ${parsed.error}`,
                              isStreaming: false,
                            }
                          : msg
                      )
                    );
                    break;
                  } else if (parsed.text) {
                    // 更新 AI 消息内容
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMessageId
                          ? { ...msg, content: msg.content + parsed.text }
                          : msg
                      )
                    );
                  } else if (parsed.done) {
                    // 流结束
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMessageId
                          ? { ...msg, isStreaming: false }
                          : msg
                      )
                    );
                    break;
                  }
                } catch (parseError) {
                  console.warn("Failed to parse SSE data:", data, parseError);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          // 请求被取消，不需要处理
          console.log("Request was aborted");
        } else {
          const errorMessage =
            err instanceof Error ? err.message : "发送消息失败";
          setError(errorMessage);

          // 更新 AI 消息显示错误
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessageId
                ? {
                    ...msg,
                    content: `发送失败: ${errorMessage}`,
                    isStreaming: false,
                  }
                : msg
            )
          );
        }
      } finally {
        setIsLoading(false);
        abortControllerRef.current = null;
      }
    },
    [isLoading, options.apiKey]
  );

  const clearMessages = useCallback(() => {
    // 取消正在进行的请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setMessages([]);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
  };
}
