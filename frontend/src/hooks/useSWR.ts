import useSWR from "swr";
import { api } from "../api/client";
import type { ItemWithSummaryListResponse, Source } from "../types/api";

// 获取数据源列表的 hook
export function useSources() {
  const { data, error, isLoading, mutate } = useSWR("sources", async () => {
    const response = await api.sources.getSources();
    if (response.error) {
      throw new Error(response.error);
    }
    return response;
  });

  return {
    sources: data?.data as Source[] | undefined,
    loading: isLoading,
    error: error?.message || data?.error,
    mutate,
  };
}

// 获取文章列表的 hook
export function useItems(
  params: {
    page?: number;
    page_size?: number;
    source_id?: string;
  } = {}
) {
  const cacheKey = `items-${JSON.stringify(params)}`;

  const { data, error, isLoading, mutate } = useSWR(cacheKey, async () => {
    const response = await api.items.getItems(params);
    if (response.error) {
      throw new Error(response.error);
    }
    return response;
  });

  return {
    items: data?.data?.items as
      | ItemWithSummaryListResponse["items"]
      | undefined,
    pagination: data?.data?.pagination as
      | ItemWithSummaryListResponse["pagination"]
      | undefined,
    loading: isLoading,
    error: error?.message || data?.error,
    mutate,
  };
}
