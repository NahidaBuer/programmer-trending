import { useState, useEffect, useRef } from "react";
import { useChat } from "../hooks/useChat";
import MessageBubble from "../components/MessageBubble";
import ChatInput from "../components/ChatInput";
import ApiKeySettings from "../components/ApiKeySettings";
import { useDiscussionStorage } from "../hooks/useDiscussionStorage";

export default function Chat() {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [rateLimitInfo, setRateLimitInfo] = useState<string>("");
  const [insertHandler, setInsertHandler] = useState<
    ((content: string) => void) | null
  >(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { count, generateMarkdown } = useDiscussionStorage();

  const { messages, isLoading, error, sendMessage, clearMessages } = useChat({
    apiKey,
  });

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 获取限流信息
  useEffect(() => {
    if (!apiKey) {
      fetch("http://localhost:8000/api/v1/chat/limits")
        .then((res) => res.json())
        .then((data) => setRateLimitInfo(data.global_limit))
        .catch(() => setRateLimitInfo(""));
    }
  }, [apiKey]);

  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  const handleClearChat = () => {
    if (window.confirm("确定要清空所有对话吗？")) {
      clearMessages();
    }
  };

  const handleInsertDiscussion = () => {
    if (insertHandler) {
      const markdown = generateMarkdown();
      insertHandler(markdown);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh)] bg-gray-50 pt-4">
      {/* 头部 */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-semibold text-gray-900">AI 对话助手</h1>

            {/* 模式指示器 */}
            <div className="flex items-center space-x-2 text-sm">
              {apiKey ? (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <svg
                    className="w-3 h-3 mr-1"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  自定义 API Key
                </span>
              ) : (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  <svg
                    className="w-3 h-3 mr-1"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                      clipRule="evenodd"
                    />
                  </svg>
                  匿名模式 {rateLimitInfo && `(${rateLimitInfo})`}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* 插入讨论清单按钮 */}
            {count > 0 && (
              <button
                onClick={handleInsertDiscussion}
                className="flex items-center space-x-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                title="插入讨论清单"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                <span>插入讨论清单 ({count})</span>
              </button>
            )}

            {/* 清空对话按钮 */}
            {messages.length > 0 && (
              <button
                onClick={handleClearChat}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                title="清空对话"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H9a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            )}

            {/* API 设置 */}
            <ApiKeySettings onApiKeyChange={setApiKey} />
          </div>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            // 欢迎界面
            <div className="flex flex-col items-center justify-center h-full text-center px-4 my-auto">
              <div className="mb-8">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-8 h-8 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  开始与 AI 对话
                </h2>
                <p className="text-gray-600 max-w-md mx-auto">
                  我是基于 Google Gemini 的 AI
                  助手，可以帮你解答问题、讨论技术话题，或分析网页内容。
                </p>
              </div>

              {/* 示例问题 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl w-full">
                {[
                  "解释一下 React 的 useEffect 原理",
                  "Python 和 JavaScript 的主要区别",
                  "什么是微服务架构？",
                  "如何优化网站性能？",
                ].map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSendMessage(question)}
                    disabled={isLoading}
                    className="p-3 text-left bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <div className="text-sm text-gray-700">{question}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            // 消息列表
            <div className="px-4 py-6">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}

              {/* 错误显示 */}
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center">
                    <svg
                      className="w-5 h-5 text-red-500 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 000 2v4a1 1 0 002 0V7a1 1 0 00-1-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="text-red-700">{error}</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* 输入区域 */}
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder={
            apiKey
              ? "输入你的问题..."
              : rateLimitInfo
              ? `输入你的问题... (${rateLimitInfo})`
              : "输入你的问题..."
          }
          onGetInsertHandler={setInsertHandler}
        />
      </div>
    </div>
  );
}
