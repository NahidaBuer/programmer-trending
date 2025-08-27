import type { ItemWithSummary } from "../types/api";

export interface DiscussionItem extends ItemWithSummary {
  addedAt: string; // 添加时间
}

const STORAGE_KEY = "discussion-list";
const MAX_ITEMS = 10;

// 创建自定义事件来同步状态
export const DISCUSSION_CHANGE_EVENT = "discussionListChanged";

// 触发自定义事件
const dispatchDiscussionChange = () => {
  window.dispatchEvent(new CustomEvent(DISCUSSION_CHANGE_EVENT));
};

export class DiscussionStorage {
  /**
   * 获取所有讨论清单项目
   */
  static getAll(): DiscussionItem[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return [];

      const items: DiscussionItem[] = JSON.parse(stored);
      // 按添加时间倒序排列（最新的在前）
      return items.sort(
        (a, b) => new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime()
      );
    } catch (error) {
      console.error("Failed to load discussion list:", error);
      return [];
    }
  }

  /**
   * 添加项目到讨论清单
   */
  static add(item: ItemWithSummary): boolean {
    try {
      const items = this.getAll();

      // 检查是否已存在（基于 id 去重）
      if (items.some((existingItem) => existingItem.id === item.id)) {
        return false; // 已存在，不添加
      }

      // 检查数量限制
      if (items.length >= MAX_ITEMS) {
        // 移除最旧的项目（数组最后一个）
        items.pop();
      }

      // 添加新项目到开头
      const discussionItem: DiscussionItem = {
        ...item,
        addedAt: new Date().toISOString(),
      };
      items.unshift(discussionItem);

      this._save(items);
      dispatchDiscussionChange(); // 触发自定义事件
      return true;
    } catch (error) {
      console.error("Failed to add item to discussion list:", error);
      return false;
    }
  }

  /**
   * 从讨论清单移除项目
   */
  static remove(itemId: number): boolean {
    try {
      const items = this.getAll();
      const filteredItems = items.filter((item) => item.id !== itemId);

      if (filteredItems.length === items.length) {
        return false; // 没有找到要删除的项目
      }

      this._save(filteredItems);
      dispatchDiscussionChange(); // 触发自定义事件
      return true;
    } catch (error) {
      console.error("Failed to remove item from discussion list:", error);
      return false;
    }
  }

  /**
   * 清空讨论清单
   */
  static clear(): boolean {
    try {
      localStorage.removeItem(STORAGE_KEY);
      dispatchDiscussionChange(); // 触发自定义事件
      return true;
    } catch (error) {
      console.error("Failed to clear discussion list:", error);
      return false;
    }
  }

  /**
   * 检查项目是否在讨论清单中
   */
  static contains(itemId: number): boolean {
    const items = this.getAll();
    return items.some((item) => item.id === itemId);
  }

  /**
   * 获取讨论清单数量
   */
  static getCount(): number {
    return this.getAll().length;
  }

  /**
   * 生成用于 Chat 的 Markdown 格式文本
   */
  static generateMarkdown(): string {
    const items = this.getAll();

    if (items.length === 0) {
      return "讨论清单为空";
    }

    let markdown = "以下是我想讨论的技术文章：\n\n";

    for (const item of items) {
      const title = item.translated_title?.trim() || item.title;
      markdown += `- ${title}`;

      // 添加翻译标题或摘要（如果不是显示标题）
      if (
        item.translated_title?.trim() &&
        item.translated_title !== item.title
      ) {
        markdown += ` (原标题: ${item.title})`;
      }
      if (item.summary_content?.trim()) {
        markdown += `\n  - 摘要：${item.summary_content.slice(0, 200)}${
          item.summary_content.length > 200 ? "..." : ""
        }`;
      }

      markdown += `\n  - 原文：${item.url}`;

      // 添加讨论链接（如果是 Hacker News）
      if (item.source_id === "hackernews") {
        markdown += `\n  - 讨论：https://news.ycombinator.com/item?id=${item.id}`;
      }

      markdown += "\n\n";
    }

    return markdown.trim();
  }

  /**
   * 导出讨论清单（JSON 格式）
   */
  static export(): string {
    const items = this.getAll();
    return JSON.stringify(items, null, 2);
  }

  /**
   * 导入讨论清单（JSON 格式）
   */
  static import(jsonData: string): boolean {
    try {
      const items: DiscussionItem[] = JSON.parse(jsonData);

      // 验证数据格式
      if (!Array.isArray(items)) {
        throw new Error("Invalid data format: expected array");
      }

      // 验证每个项目的基本字段
      for (const item of items) {
        if (!item.id || !item.title || !item.url || !item.addedAt) {
          throw new Error("Invalid item format");
        }
      }

      // 保存（会自动限制数量和去重）
      this._save(items.slice(0, MAX_ITEMS));
      return true;
    } catch (error) {
      console.error("Failed to import discussion list:", error);
      return false;
    }
  }

  /**
   * 私有方法：保存到 localStorage
   */
  private static _save(items: DiscussionItem[]): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }
}

// 监听存储变化的Hook接口
export interface UseDiscussionStorageReturn {
  items: DiscussionItem[];
  count: number;
  add: (item: ItemWithSummary) => boolean;
  remove: (itemId: number) => boolean;
  clear: () => boolean;
  contains: (itemId: number) => boolean;
  generateMarkdown: () => string;
}
