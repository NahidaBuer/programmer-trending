import type { ItemWithSummary } from "../types/api";
import { formatTimeAgo, getSourceDisplayName, getDiscussionUrl } from "../utils/itemHelpers";

interface ItemMetaProps {
  item: ItemWithSummary;
  showScore?: boolean;
  showAuthor?: boolean;
  showSource?: boolean;
  showTime?: boolean;
  timeField?: "created_at" | "addedAt"; // 支持不同的时间字段
  timePrefix?: string;
  size?: "small" | "medium";
  className?: string;
}

/**
 * 可复用的文章元信息组件
 * 灵活配置显示哪些信息
 */
export default function ItemMeta({
  item,
  showScore = true,
  showAuthor = true,
  showSource = true,
  showTime = true,
  timeField = "created_at",
  timePrefix = "",
  size = "medium",
  className = "",
}: ItemMetaProps) {
  const sizeClasses = {
    small: "text-xs",
    medium: "text-sm"
  };

  const baseClassName = `flex items-center text-gray-500 space-x-4 ${sizeClasses[size]} ${className}`;

  return (
    <div className={baseClassName}>
      {/* 分数 */}
      {showScore && item.score !== undefined && (
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
      {showAuthor && item.author && <span>by {item.author}</span>}

      {/* 数据源 */}
      {showSource && (
        <a
          href={getDiscussionUrl(item)}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-blue-600"
        >
          <span>{getSourceDisplayName(item.source_id)}</span>
        </a>
      )}

      {/* 时间 */}
      {showTime && (
        <span>
          {timePrefix}{formatTimeAgo((item as any)[timeField])}
        </span>
      )}
    </div>
  );
}