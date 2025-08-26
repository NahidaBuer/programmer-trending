import { useState } from "react";
import { useDiscussionStorage } from "../hooks/useDiscussionStorage";
import DiscussionListModal from "./DiscussionListModal";

export default function DiscussionCartButton() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { count } = useDiscussionStorage();

  return (
    <>
      {/* 悬浮按钮 */}
      <button
        onClick={() => setIsModalOpen(true)}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all duration-200 z-50 group"
        aria-label="查看讨论清单"
      >
        <div className="relative">
          {/* 聊天图标 */}
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>

          {/* 数量徽标 */}
          {count > 0 && (
            <span className="absolute -top-4 -right-4 bg-red-500 text-white text-xs font-medium rounded-full h-6 w-6 flex items-center justify-center min-w-[1.5rem]">
              {count > 99 ? "99+" : count}
            </span>
          )}
        </div>

        {/* 悬停提示 */}
        <div className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-sm py-2 px-3 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
          讨论清单 ({count})
          <div className="absolute left-full top-1/2 -translate-y-1/2 border-4 border-transparent border-l-gray-900"></div>
        </div>
      </button>

      {/* 弹窗 */}
      <DiscussionListModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}
