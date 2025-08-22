// API 客户端封装

import type { 
  APIResponse, 
  ItemWithSummaryListResponse,
  Source,
  ChatMessage,
  ChatResponse 
} from '../types/api';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 通用 API 请求函数
async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<APIResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    return {
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      meta: { requestId: 'unknown' }
    };
  }
}

// 文章相关 API
export const itemsApi = {
  // 获取文章列表（带摘要）
  async getItems(params: {
    page?: number;
    page_size?: number;
    source_id?: string;
  } = {}): Promise<APIResponse<ItemWithSummaryListResponse>> {
    const searchParams = new URLSearchParams();
    
    if (params.page) searchParams.set('page', params.page.toString());
    if (params.page_size) searchParams.set('page_size', params.page_size.toString());
    if (params.source_id) searchParams.set('source_id', params.source_id);
    
    const query = searchParams.toString();
    const endpoint = `/items${query ? `?${query}` : ''}`;
    
    return apiRequest<ItemWithSummaryListResponse>(endpoint);
  },
};

// 数据源相关 API
export const sourcesApi = {
  // 获取数据源列表
  async getSources(): Promise<APIResponse<Source[]>> {
    return apiRequest<Source[]>('/sources');
  },
};

// 聊天相关 API
export const chatApi = {
  // 发送聊天消息
  async sendMessage(message: ChatMessage): Promise<APIResponse<ChatResponse>> {
    return apiRequest<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(message),
    });
  },
};

// 导出所有 API
export const api = {
  items: itemsApi,
  sources: sourcesApi,
  chat: chatApi,
};