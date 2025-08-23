import type { ItemWithSummary } from "../types/api";

interface ItemCardProps {
  item: ItemWithSummary;
}

// 格式化时间显示
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

// 获取摘要状态显示
function getSummaryStatusDisplay(
  status?: string
): { text: string; className: string } | null {
  switch (status) {
    case "pending":
      return { text: "等待摘要", className: "bg-yellow-100 text-yellow-800" };
    case "in_progress":
      return { text: "生成中", className: "bg-blue-100 text-blue-800" };
    case "completed":
      return null; // 完成状态不显示badge
    case "failed":
      return { text: "摘要失败", className: "bg-red-100 text-red-800" };
    case "permanently_failed":
      return { text: "摘要不可用", className: "bg-gray-100 text-gray-800" };
    default:
      return null;
  }
}

export default function ItemCard({ item }: ItemCardProps) {
  // 智能标题显示：优先显示翻译标题，无则回落到原始标题
  const displayTitle = item.translated_title?.trim() || item.title;

  // 摘要状态显示
  const summaryStatus = getSummaryStatusDisplay(item.summary_status);

  return (
    <article className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* 标题和链接 */}
      <div className="mb-3">
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors line-clamp-2"
        >
          {displayTitle}
        </a>
        {/* 如果显示的是翻译标题，小字显示原标题 */}
        {item.translated_title?.trim() &&
          item.translated_title !== item.title && (
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

          {/* 数据源 */}
          <a href={item.url} target="_blank" rel="noopener noreferrer">
            <span className="capitalize hover:text-blue-600">
              {item.source_id}
            </span>
          </a>
        </div>

        {/* 时间 */}
        <a href={item.url} target="_blank" rel="noopener noreferrer">
          <span className="hover:text-blue-600">
            {formatTimeAgo(item.created_at)}
          </span>
        </a>
      </div>
    </article>
  );
}
