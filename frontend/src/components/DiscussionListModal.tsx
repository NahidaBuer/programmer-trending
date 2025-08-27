import { useEffect, useState } from "react";
import { useDiscussionStorage } from "../hooks/useDiscussionStorage";
import { useNavigate } from "react-router-dom";
import {
  formatTimeAgo,
  getSourceDisplayName,
  getDisplayTitle,
  hasTranslatedTitle,
} from "../utils/itemHelpers";

interface DiscussionListModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function DiscussionListModal({
  isOpen,
  onClose,
}: DiscussionListModalProps) {
  const { items, remove, clear } = useDiscussionStorage();
  const navigate = useNavigate();
  const [showTooltip, setShowTooltip] = useState(false);

  // ESC 键关闭弹窗
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden"; // 禁止背景滚动
    }

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  const handleGoToChat = () => {
    onClose();
    navigate("/chat");
  };

  const handleClearAll = () => {
    if (window.confirm("确定要清空讨论清单吗？")) {
      clear();
    }
  };

  const handleRemoveItem = (itemId: number) => {
    remove(itemId);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[95vh] overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3 cursor-pointer relative">
            <div
              className="flex items-center space-x-3"
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
            >
              <h2 className="text-xl font-semibold text-gray-900">讨论清单</h2>
              <span className="inline-flex items-center bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded-full">
                {items.length} 项
              </span>
              <svg
                className="w-4 h-4 text-gray-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>

            {/* Tooltip */}
            {showTooltip && (
              <div className="absolute left-0 top-full mt-2 bg-gray-900 text-white text-sm rounded-lg py-2 px-3 shadow-lg z-50 whitespace-nowrap">
                <div className="space-y-1">
                  <div>• 收集感兴趣的文章用于 AI 对话讨论</div>
                  <div>• 最多保存 10 条，超出时自动删除最旧的</div>
                  <div>• 可在聊天页面插入为对话背景</div>
                </div>
                {/* 箭头 */}
                <div className="absolute -top-1 left-4 w-2 h-2 bg-gray-900 rotate-45"></div>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {items.length > 0 && (
              <>
                <button
                  onClick={handleGoToChat}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  去聊天页面
                </button>
                <button
                  onClick={handleClearAll}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                >
                  清空全部
                </button>
              </>
            )}
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 p-2"
              aria-label="关闭"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* 内容 */}
        <div className="overflow-y-auto max-h-[90vh]">
          {items.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <svg
                className="w-12 h-12 mx-auto mb-4 text-gray-300"
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
              <p>讨论清单为空</p>
              <p className="text-sm mt-1">
                在文章列表中点击"加入讨论"来添加感兴趣的文章
              </p>
            </div>
          ) : (
            <div className="p-6 space-y-4">
              {items.map((item) => {
                const displayTitle = getDisplayTitle(item);

                return (
                  <div
                    key={item.id}
                    className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        {/* 标题 */}
                        <div className="mb-2">
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-lg font-medium text-gray-900 hover:text-blue-600 transition-colors line-clamp-2"
                          >
                            {displayTitle}
                          </a>
                          {/* 如果显示的是翻译标题，小字显示原标题 */}
                          {hasTranslatedTitle(item) && (
                            <p className="text-sm text-gray-500 mt-1 line-clamp-1">
                              {item.title}
                            </p>
                          )}
                        </div>

                        {/* 摘要 */}
                        {item.summary_content && (
                          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                            {item.summary_content}
                          </p>
                        )}

                        {/* 元信息 */}
                        <div className="flex items-center text-xs text-gray-500 space-x-4">
                          <span>{getSourceDisplayName(item.source_id)}</span>
                          {item.author && <span>by {item.author}</span>}
                          <span>添加于 {formatTimeAgo(item.addedAt)}</span>
                        </div>
                      </div>

                      {/* 删除按钮 */}
                      <button
                        onClick={() => handleRemoveItem(item.id)}
                        className="ml-4 text-gray-400 hover:text-red-600 transition-colors p-1"
                        aria-label="移除"
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
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* 底部提示 */}
        {items.length > 0 && (
          <div className="p-4 bg-gray-50 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center">
              在聊天页面中，点击"插入讨论清单"按钮可以快速将这些文章作为上下文发送给
              AI
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
