import type { ItemWithSummary } from "../types/api";
import { getDisplayTitle, hasTranslatedTitle } from "../utils/itemHelpers";

interface ItemTitleProps {
  item: ItemWithSummary;
  size?: "small" | "medium" | "large";
  showOriginalTitle?: boolean;
  className?: string;
  linkClassName?: string;
  originalTitleClassName?: string;
}

/**
 * 可复用的文章标题组件
 * 支持不同尺寸、可选显示原标题
 */
export default function ItemTitle({
  item,
  size = "medium",
  showOriginalTitle = true,
  className = "",
  linkClassName = "",
  originalTitleClassName = "",
}: ItemTitleProps) {
  const displayTitle = getDisplayTitle(item);
  
  const sizeClasses = {
    small: "text-sm font-medium",
    medium: "text-lg font-semibold", 
    large: "text-xl font-bold"
  };

  const baseLinkClasses = "text-gray-900 hover:text-blue-600 transition-colors line-clamp-2";
  const finalLinkClassName = `${sizeClasses[size]} ${baseLinkClasses} ${linkClassName}`;
  
  const baseOriginalClasses = "text-sm text-gray-500 mt-1 line-clamp-1";
  const finalOriginalClassName = `${baseOriginalClasses} ${originalTitleClassName}`;

  return (
    <div className={className}>
      <a
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className={finalLinkClassName}
      >
        {displayTitle}
      </a>
      
      {/* 如果显示的是翻译标题，小字显示原标题 */}
      {showOriginalTitle && hasTranslatedTitle(item) && (
        <p className={finalOriginalClassName}>
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
  );
}