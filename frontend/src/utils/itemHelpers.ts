import type { ItemWithSummary } from "../types/api";

/**
 * 格式化时间显示
 */
export function formatTimeAgo(dateString: string): string {
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

/**
 * 数据源名称映射
 */
export function getSourceDisplayName(sourceId: string): string {
  const sourceNames: Record<string, string> = {
    hackernews: "Hacker News",
    github: "GitHub",
  };
  return sourceNames[sourceId] || sourceId;
}

/**
 * 生成讨论链接
 */
export function getDiscussionUrl(item: ItemWithSummary): string {
  if (item.source_id === "hackernews") {
    return `https://news.ycombinator.com/item?id=${item.source_internal_id}`;
  }
  return item.url;
}

/**
 * 获取智能标题显示（优先翻译标题）
 */
export function getDisplayTitle(item: ItemWithSummary): string {
  return item.translated_title?.trim() || item.title;
}

/**
 * 判断是否有翻译标题且与原标题不同
 */
export function hasTranslatedTitle(item: ItemWithSummary): boolean {
  return Boolean(
    item.translated_title?.trim() && item.translated_title !== item.title
  );
}

/**
 * 摘要状态显示配置
 */
export function getSummaryStatusDisplay(
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
