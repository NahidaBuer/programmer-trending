import { useState, useRef, useEffect, useCallback } from "react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  onGetInsertHandler?: (handler: (content: string) => void) => void; // 获取插入处理器的回调
}

export default function ChatInput({
  onSendMessage,
  disabled = false,
  placeholder = "输入你的问题...",
  onGetInsertHandler,
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 自动调整文本框高度
  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
    }
  };

  useEffect(() => {
    adjustHeight();
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message?.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
  };

  // 插入内容的方法
  const insertContent = useCallback((content: string) => {
    setMessage(currentMessage => {
      const newMessage = currentMessage ? `${currentMessage}\n\n${content}` : content;
      
      // 设置焦点到文本框并移动光标到末尾
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.focus();
          textareaRef.current.setSelectionRange(newMessage.length, newMessage.length);
        }
      }, 0);
      
      return newMessage;
    });
  }, []);

  // 暴露插入方法给父组件
  useEffect(() => {
    if (onGetInsertHandler) {
      onGetInsertHandler(insertContent);
    }
  }, [onGetInsertHandler, insertContent]);

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onCompositionStart={handleCompositionStart}
            onCompositionEnd={handleCompositionEnd}
            placeholder={disabled ? "AI 正在回复中..." : (placeholder || "输入你的问题...")}
            disabled={disabled}
            className={`
              w-full resize-none rounded-lg border border-gray-300 px-4 py-3 pr-12
              focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500
              disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
              transition-colors duration-200
              min-h-[50px] max-h-[120px]
            `}
            rows={1}
          />

          {/* 发送按钮 */}
          <button
            type="submit"
            disabled={disabled || !message?.trim()}
            className={`
              absolute right-2 bottom-2 p-2 rounded-lg transition-all duration-200
              ${
                disabled || !message?.trim()
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                  : "bg-blue-600 text-white hover:bg-blue-700 active:scale-95"
              }
            `}
          >
            {disabled ? (
              // 加载动画
              <svg
                className="w-5 h-5 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            ) : (
              // 发送图标
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
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </button>
        </div>
      </form>

      {/* 提示文字 */}
      <div className="mt-2 text-xs text-gray-500 text-center">
        按 Enter 发送，Shift + Enter 换行
      </div>
    </div>
  );
}
