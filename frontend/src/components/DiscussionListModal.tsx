import { useEffect } from "react";
import { useDiscussionStorage } from "../hooks/useDiscussionStorage";
import { useNavigate } from "react-router-dom";

interface DiscussionListModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// 格式化时间显示（复制自 ItemCard）
function formatTimeAgo(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diffInHours = Math.floor(
    (now.getTime() - date.getTime()) / (1000 * 60 * 60)
  );

  if (diffInHours < 1) return "刚刚";
  if (diffInHours < 24) return `${diffInHours}小时前`;

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) return `${diffInDays}天前`;

  const diffInMonths = Math.floor(diffInDays / 30);
  return `${diffInMonths}个月前`;
}

// 数据源名称映射（复制自 ItemCard）
function getSourceDisplayName(sourceId: string): string {
  const sourceNames: Record<string, string> = {
    hackernews: "Hacker News",
    github: "GitHub",
    reddit: "Reddit",
    producthunt: "Product Hunt",
  };
  return sourceNames[sourceId] || sourceId;
}

export default function DiscussionListModal({
  isOpen,
  onClose,
}: DiscussionListModalProps) {
  const { items, remove, clear } = useDiscussionStorage();
  const navigate = useNavigate();

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
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-semibold text-gray-900">讨论清单</h2>
            <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded-full">
              {items.length} 项
            </span>
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
                const displayTitle =
                  item.translated_title?.trim() || item.title;

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
                          {item.translated_title?.trim() &&
                            item.translated_title !== item.title && (
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
