import useSWR from 'swr';
import type { ItemWithSummaryListResponse, Source } from '../types/api';

// SWR fetcher 函数
const fetcher = async (url: string) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// 获取数据源列表的 hook
export function useSources() {
  const { data, error, isLoading, mutate } = useSWR(
    'http://localhost:8000/api/v1/sources',
    fetcher
  );

  return {
    sources: data?.data as Source[] | undefined,
    loading: isLoading,
    error: error || data?.error,
    mutate,
  };
}

// 获取文章列表的 hook
export function useItems(params: {
  page?: number;
  page_size?: number;
  source_id?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  
  if (params.page) searchParams.set('page', params.page.toString());
  if (params.page_size) searchParams.set('page_size', params.page_size.toString());
  if (params.source_id) searchParams.set('source_id', params.source_id);
  
  const query = searchParams.toString();
  const url = `http://localhost:8000/api/v1/items${query ? `?${query}` : ''}`;
  
  const { data, error, isLoading, mutate } = useSWR(url, fetcher);

  return {
    items: data?.data?.items as ItemWithSummaryListResponse['items'] | undefined,
    pagination: data?.data?.pagination as ItemWithSummaryListResponse['pagination'] | undefined,
    loading: isLoading,
    error: error || data?.error,
    mutate,
  };
}