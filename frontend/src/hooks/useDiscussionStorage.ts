import { useState, useEffect, useCallback } from "react";
import { 
  DiscussionStorage, 
  DISCUSSION_CHANGE_EVENT,
  type DiscussionItem, 
  type UseDiscussionStorageReturn 
} from "../utils/discussionStorage";
import type { ItemWithSummary } from "../types/api";

/**
 * 讨论清单管理 Hook
 * 提供响应式的讨论清单状态管理
 */
export function useDiscussionStorage(): UseDiscussionStorageReturn {
  const [items, setItems] = useState<DiscussionItem[]>([]);
  const [count, setCount] = useState(0);

  // 从 localStorage 加载数据
  const loadItems = useCallback(() => {
    const loadedItems = DiscussionStorage.getAll();
    setItems(loadedItems);
    setCount(loadedItems.length);
  }, []);

  // 初始化加载
  useEffect(() => {
    loadItems();
  }, [loadItems]);

  // 监听讨论清单变化（包括同一页面内的变化）
  useEffect(() => {
    const handleDiscussionChange = () => {
      loadItems();
    };

    // 监听自定义事件（同一页面内的变化）
    window.addEventListener(DISCUSSION_CHANGE_EVENT, handleDiscussionChange);
    
    // 仍然监听 storage 事件（跨窗口的变化）
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "discussion-list") {
        loadItems();
      }
    };
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener(DISCUSSION_CHANGE_EVENT, handleDiscussionChange);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [loadItems]);

  const add = useCallback((item: ItemWithSummary): boolean => {
    return DiscussionStorage.add(item);
    // 不需要手动 loadItems()，自定义事件会自动触发更新
  }, []);

  const remove = useCallback((itemId: number): boolean => {
    return DiscussionStorage.remove(itemId);
    // 不需要手动 loadItems()，自定义事件会自动触发更新
  }, []);

  const clear = useCallback((): boolean => {
    return DiscussionStorage.clear();
    // 不需要手动 loadItems()，自定义事件会自动触发更新
  }, []);

  const contains = useCallback((itemId: number): boolean => {
    return items.some(item => item.id === itemId);
  }, [items]);

  const generateMarkdown = useCallback((): string => {
    return DiscussionStorage.generateMarkdown();
  }, []);

  return {
    items,
    count,
    add,
    remove,
    clear,
    contains,
    generateMarkdown,
  };
}