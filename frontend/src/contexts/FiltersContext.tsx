import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";

// 筛选器类型定义
export type SummaryFilterType = "all" | "with_summary" | "without_summary";
export type SortFilterType = "score" | "time";

export interface FilterParams {
  timeFilter: number | "custom" | undefined;
  summaryFilter: SummaryFilterType;
  sortFilter: SortFilterType;
  customDays: string;
}

// 默认筛选器状态
const DEFAULT_FILTERS: FilterParams = {
  timeFilter: undefined,
  summaryFilter: "all",
  sortFilter: "score",
  customDays: "",
};

// Context 类型定义
interface FiltersContextType {
  filters: FilterParams;
  updateFilter: <K extends keyof FilterParams>(
    key: K,
    value: FilterParams[K]
  ) => void;
  resetFilters: () => void;
  // 计算实际的API参数
  getAPIParams: () => {
    days?: number;
    has_summary?: boolean;
    sort_by: "score" | "time";
  };
}

// 创建 Context
const FiltersContext = createContext<FiltersContextType | null>(null);

// Provider 组件
export const FiltersProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [filters, setFilters] = useState<FilterParams>(DEFAULT_FILTERS);

  // 更新单个筛选器的值
  const updateFilter = useCallback(
    <K extends keyof FilterParams>(key: K, value: FilterParams[K]) => {
      setFilters((prev) => ({
        ...prev,
        [key]: value,
      }));
    },
    []
  );

  // 重置所有筛选器
  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  // 计算实际的API参数
  const getAPIParams = useCallback((): {
    days?: number;
    has_summary?: boolean;
    sort_by: "score" | "time";
  } => {
    const actualDays =
      filters.timeFilter === "custom"
        ? filters.customDays && !isNaN(Number(filters.customDays))
          ? Number(filters.customDays)
          : undefined
        : filters.timeFilter;

    const actualHasSummary =
      filters.summaryFilter === "all"
        ? undefined
        : filters.summaryFilter === "with_summary"
        ? true
        : false;

    return {
      days: actualDays,
      has_summary: actualHasSummary,
      sort_by: filters.sortFilter as "score" | "time",
    };
  }, [filters]);

  const contextValue: FiltersContextType = {
    filters,
    updateFilter,
    resetFilters,
    getAPIParams,
  };

  return (
    <FiltersContext.Provider value={contextValue}>
      {children}
    </FiltersContext.Provider>
  );
};

// 自定义 hook 用于使用 Context
export const useFilters = (): FiltersContextType => {
  const context = useContext(FiltersContext);
  if (!context) {
    throw new Error("useFilters must be used within a FiltersProvider");
  }
  return context;
};
