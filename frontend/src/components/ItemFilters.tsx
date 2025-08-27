import React, { memo } from "react";
import { useFilters, type SummaryFilterType } from "../contexts/FiltersContext";

// 时间筛选选项
const TIME_FILTER_OPTIONS = [
  { label: "1天", value: 1 },
  { label: "7天", value: 7 },
  { label: "30天", value: 30 },
  { label: "全部", value: undefined },
  { label: "自定义", value: "custom" as const },
];

// 摘要状态筛选选项
const SUMMARY_FILTER_OPTIONS = {
  with_summary: { label: "仅显示有摘要", has_summary: true },
  all: { label: "显示全部", has_summary: undefined },
  without_summary: { label: "仅显示无摘要", has_summary: false },
};

// 排序选项
const SORT_FILTER_OPTIONS = {
  time: { label: "按时间", value: "time" },
  score: { label: "按点赞数", value: "score" },
};

// 使用 memo 防止不必要的重渲染，现在只有Context中的filters变化才会重渲染
const ItemFilters: React.FC = memo(() => {
  const { filters, updateFilter } = useFilters();
  const { timeFilter, summaryFilter, sortFilter, customDays } = filters;

  const handleTimeFilterChange = (value: number | "custom" | undefined) => {
    updateFilter("timeFilter", value);
    if (value !== "custom") {
      updateFilter("customDays", "");
    }
  };

  const handleSummaryFilterChange = () => {
    const filterOrder: SummaryFilterType[] = [
      "all",
      "with_summary",
      "without_summary",
    ];
    const currentIndex = filterOrder.indexOf(summaryFilter);
    const nextIndex = (currentIndex + 1) % filterOrder.length;
    updateFilter("summaryFilter", filterOrder[nextIndex]);
  };

  const handleSortFilterChange = () => {
    const newSort = sortFilter === "score" ? "time" : "score";
    updateFilter("sortFilter", newSort);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div className="flex flex-wrap items-center gap-6">
        {/* 时间筛选器 */}
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-700">时间范围:</span>
          <div className="flex items-center gap-2">
            {TIME_FILTER_OPTIONS.map((option) => (
              <label key={option.label} className="flex items-center">
                <input
                  type="radio"
                  name="timeFilter"
                  value={
                    option.value === "custom" ? "custom" : option.value || ""
                  }
                  checked={timeFilter === option.value}
                  onChange={() => handleTimeFilterChange(option.value)}
                  className="mr-1 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
            {timeFilter === "custom" && (
              <input
                type="number"
                placeholder="天数"
                value={customDays}
                onChange={(e) => updateFilter("customDays", e.target.value)}
                className="ml-1 px-2 py-1 border border-gray-300 rounded text-sm w-16 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                min="1"
                max="365"
              />
            )}
          </div>
        </div>

        {/* 排序筛选器 */}
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-700">排序:</span>
          <button
            onClick={handleSortFilterChange}
            className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1 bg-green-100 text-green-800 hover:bg-green-200"
          >
            {SORT_FILTER_OPTIONS[sortFilter].label}
            <svg
              className="ml-1 w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
              />
            </svg>
          </button>
        </div>

        {/* 摘要筛选器 */}
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-700">AI摘要:</span>
          <button
            onClick={handleSummaryFilterChange}
            className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 bg-blue-100 text-blue-800 hover:bg-blue-200"
          >
            {SUMMARY_FILTER_OPTIONS[summaryFilter].label}
            <svg
              className="ml-1 w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 9l4-4 4 4m0 6l-4 4-4-4"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
});

ItemFilters.displayName = "ItemFilters";

export default ItemFilters;
