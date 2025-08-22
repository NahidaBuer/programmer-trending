import { useState, useEffect } from "react";
import { useItems } from "../hooks/useSWR";
import ItemCard from "./ItemCard";
import type { PaginationMeta } from "../types/api";

interface ItemListProps {
  sourceId?: string;
}

// 分页组件
function Pagination({
  pagination,
  onPageChange,
}: {
  pagination: PaginationMeta;
  onPageChange: (page: number) => void;
}) {
  const { page, total_pages, has_prev, has_next } = pagination;

  // 生成页码数组（显示当前页前后各2页）
  const getPageNumbers = () => {
    const pages: number[] = [];
    const start = Math.max(1, page - 2);
    const end = Math.min(total_pages, page + 2);

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    return pages;
  };

  if (total_pages <= 1) return null;

  return (
    <div className="flex items-center justify-center space-x-2 mt-8">
      {/* 上一页 */}
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={!has_prev}
        className={`px-3 py-2 rounded-md text-sm font-medium ${
          has_prev
            ? "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 cursor-pointer"
            : "bg-gray-100 text-gray-400 border border-gray-300 cursor-not-allowed"
        }`}
      >
        上一页
      </button>

      {/* 页码 */}
      {getPageNumbers().map((pageNum) => (
        <button
          key={pageNum}
          onClick={() => onPageChange(pageNum)}
          className={`px-3 py-2 rounded-md text-sm font-medium ${
            pageNum === page
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 cursor-pointer"
          }`}
        >
          {pageNum}
        </button>
      ))}

      {/* 下一页 */}
      <button
        onClick={() => onPageChange(page + 1)}
        disabled={!has_next}
        className={`px-3 py-2 rounded-md text-sm font-medium ${
          has_next
            ? "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 cursor-pointer"
            : "bg-gray-100 text-gray-400 border border-gray-300 cursor-not-allowed"
        }`}
      >
        下一页
      </button>
    </div>
  );
}

// 加载骨架屏
function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      {Array.from({ length: 5 }).map((_, index) => (
        <div
          key={index}
          className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse"
        >
          <div className="h-6 bg-gray-200 rounded mb-3"></div>
          <div className="h-4 bg-gray-200 rounded mb-2 w-3/4"></div>
          <div className="h-20 bg-gray-100 rounded mb-4"></div>
          <div className="flex justify-between">
            <div className="h-4 bg-gray-200 rounded w-32"></div>
            <div className="h-4 bg-gray-200 rounded w-20"></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function ItemList({ sourceId }: ItemListProps) {
  const [currentPage, setCurrentPage] = useState(1);

  // 使用 SWR 获取文章列表
  const { items, pagination, loading, error, mutate } = useItems({
    page: currentPage,
    page_size: 20,
    source_id: sourceId,
  });

  // 翻页处理
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // 数据源切换时重置页码
  useEffect(() => {
    setCurrentPage(1);
  }, [sourceId]);

  const handleRetry = () => {
    mutate();
  };

  // 错误状态
  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <svg
            className="w-12 h-12 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">加载失败</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={handleRetry}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          重试
        </button>
      </div>
    );
  }

  // 加载状态
  if (loading) {
    return <LoadingSkeleton />;
  }

  // 空状态
  if (!loading && (!items || items.length === 0)) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg
            className="w-12 h-12 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">暂无内容</h3>
        <p className="text-gray-600">当前数据源暂时没有文章，请稍后再试</p>
      </div>
    );
  }

  return (
    <div>
      {/* 文章列表 */}
      <div className="space-y-6">
        {items?.map((item) => (
          <ItemCard key={item.id} item={item} />
        ))}
      </div>

      {/* 分页 */}
      {pagination && (
        <Pagination pagination={pagination} onPageChange={handlePageChange} />
      )}
    </div>
  );
}
