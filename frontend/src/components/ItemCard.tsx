import { useState } from "react";
import type { ItemWithSummary } from "../types/api";
import { useDiscussionStorage } from "../hooks/useDiscussionStorage";
import { 
  formatTimeAgo, 
  getSourceDisplayName, 
  getDiscussionUrl, 
  getDisplayTitle,
  hasTranslatedTitle,
  getSummaryStatusDisplay
} from "../utils/itemHelpers";

interface ItemCardProps {
  item: ItemWithSummary;
}


export default function ItemCard({ item }: ItemCardProps) {
  const [showToast, setShowToast] = useState(false);
  const [isToastFading, setIsToastFading] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const { add, remove, contains } = useDiscussionStorage();

  // 智能标题显示：优先显示翻译标题，无则回落到原始标题
  const displayTitle = getDisplayTitle(item);

  // 摘要状态显示
  const summaryStatus = getSummaryStatusDisplay(item.summary_status);

  // 检查是否已在讨论清单中
  const isInDiscussion = contains(item.id);

  // 处理添加到讨论清单
  const handleAddToDiscussion = () => {
    const success = add(item);
    if (success) {
      showToastMessage("已添加到讨论清单");
    } else {
      showToastMessage("添加失败或已存在");
    }
  };

  // 处理从讨论清单移除
  const handleRemoveFromDiscussion = () => {
    const success = remove(item.id);
    if (success) {
      showToastMessage("已从讨论清单移除");
    }
  };

  // 显示 Toast 提示
  const showToastMessage = (message: string) => {
    setToastMessage(message);
    setShowToast(true);
    setIsToastFading(false);
    
    // 开始淡出
    setTimeout(() => {
      setIsToastFading(true);
    }, 1500);
    
    // 完全隐藏
    setTimeout(() => {
      setShowToast(false);
      setIsToastFading(false);
    }, 2000);
  };

  return (
    <article className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow relative">
      {/* Toast 提示 */}
      {showToast && (
        <div className={`absolute top-2 right-2 bg-green-500 text-white px-3 py-1 rounded-lg text-sm z-10 transition-all duration-300 ${
          isToastFading ? 'opacity-0 translate-y-2' : 'opacity-100 translate-y-0 animate-fade-in'
        }`}>
          {toastMessage}
        </div>
      )}
      {/* 标题和操作按钮区域 */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors line-clamp-2"
          >
            {displayTitle}
          </a>
          {/* 如果显示的是翻译标题，小字显示原标题 */}
          {hasTranslatedTitle(item) && (
              <p className="text-sm text-gray-500 mt-1 line-clamp-1">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600"
                >
                  {item.title}
                </a>
              </p>
            )}
        </div>

        {/* 讨论按钮 */}
        <button
          onClick={
            isInDiscussion ? handleRemoveFromDiscussion : handleAddToDiscussion
          }
          className={`ml-3 px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
            isInDiscussion
              ? "bg-red-100 text-red-700 hover:bg-red-200"
              : "bg-blue-100 text-blue-700 hover:bg-blue-200"
          }`}
          title={isInDiscussion ? "从讨论清单移除" : "加入讨论清单"}
        >
          {isInDiscussion ? "移除" : "讨论"}
        </button>
      </div>
      {/* AI 摘要 */}
      {(item.summary_content && (
        <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div className="flex items-center mb-2">
            <span className="text-sm font-medium text-blue-400">AI 摘要</span>
          </div>
          <p className="text-gray-700 text-sm leading-relaxed">
            {item.summary_content}
          </p>
        </div>
      )) ||
        (!summaryStatus && (
          <div className="mb-4 p-4 bg-red-50 rounded-lg border border-red-100">
            <p className="text-gray-700 text-sm leading-relaxed">
              AI 摘要暂不可用，可能受到源站严格反爬限制
            </p>
          </div>
        ))}{" "}
      {/* 如果摘要状态完成且为空，解释一下（ */}
      {/* 摘要状态（如果不是完成状态） */}
      {summaryStatus && (
        <div className="mb-4">
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${summaryStatus.className}`}
          >
            {summaryStatus.text}
          </span>
        </div>
      )}
      {/* 元信息 */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center space-x-4">
          {/* 分数 */}
          {item.score !== undefined && (
            <span className="flex items-center">
              <svg
                className="w-4 h-4 mr-1"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              {item.score}
            </span>
          )}

          {/* 作者 */}
          {item.author && <span>by {item.author}</span>}

          {/* 数据源和讨论链接 */}
          <a
            href={getDiscussionUrl(item)}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-blue-600"
          >
            <span>{getSourceDisplayName(item.source_id)}</span>
          </a>
          {/* 时间 */}
        </div>
        <span className="ml-2">{formatTimeAgo(item.created_at)}</span>
      </div>
    </article>
  );
}
