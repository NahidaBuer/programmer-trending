// API 类型定义，对应后端 Pydantic 模型
// backend/app/schemas
export interface APIResponse<T> {
  data: T | null;
  error: string | null;
  meta: {
    requestId: string;
  };
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// 摘要状态枚举
export type SummaryStatus =
  | "pending"
  | "in_progress"
  | "completed"
  | "failed"
  | "permanently_failed"
  | "skipped";

// 带摘要信息的文章
export interface ItemWithSummary {
  id: number;
  source_id: string;
  title: string;
  url: string;
  score?: number;
  author?: string;
  created_at: string;
  fetched_at: string;
  // 摘要相关字段
  summary_content?: string;
  translated_title?: string;
  summary_status?: SummaryStatus;
}

// 文章列表响应
export interface ItemWithSummaryListResponse {
  items: ItemWithSummary[];
  pagination: PaginationMeta;
}

// 数据源
export interface Source {
  id: string;
  name: string;
  description?: string;
  base_url: string;
  enabled: boolean;
  created_at: string;
}

// 聊天相关
export interface ChatMessage {
  content: string;
  context_url?: string;
}

export interface ChatResponse {
  reply: string;
  response_json?: any;
}
