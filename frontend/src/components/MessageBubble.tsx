import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "prismjs/themes/prism-tomorrow.css";

export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  isStreaming?: boolean;
}

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  // 格式化时间
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // 用户消息样式
  if (message.isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[70%] group">
          <div className="bg-blue-600 text-white rounded-2xl rounded-tr-md px-4 py-3">
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-1 text-right opacity-0 group-hover:opacity-100 transition-opacity">
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    );
  }

  // AI 回复样式
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[85%] group">
        <div className="flex items-start space-x-3">
          {/* AI 头像 */}
          <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mt-1">
            <img src="/gemini-color.svg" alt="Gemini AI" className="w-5 h-5" />
          </div>

          {/* 消息内容 */}
          <div className="flex-1">
            <div className="bg-gray-100 rounded-2xl rounded-tl-md px-4 py-3 relative">
              {message.isStreaming && (
                <div className="absolute top-2 right-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              )}

              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight]}
                  components={{
                    // 自定义代码块样式
                    code: ({ className, children, ...props }) => {
                      const isInline = !className;
                      if (isInline) {
                        return (
                          <code
                            className="bg-gray-200 px-1 py-0.5 rounded text-sm font-mono"
                            {...props}
                          >
                            {children}
                          </code>
                        );
                      }
                      return (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                    // 自定义段落样式
                    p: ({ children }) => (
                      <p className="mb-2 last:mb-0 leading-relaxed">
                        {children}
                      </p>
                    ),
                    // 自定义列表样式
                    ul: ({ children }) => (
                      <ul className="mb-2 last:mb-0 pl-4">{children}</ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="mb-2 last:mb-0 pl-4">{children}</ol>
                    ),
                    // 自定义链接样式
                    a: ({ href, children }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 underline"
                      >
                        {children}
                      </a>
                    ),
                    // 自定义表格样式
                    table: ({ children }) => (
                      <div className="overflow-x-auto my-4">
                        <table className="min-w-full border-collapse border border-gray-300">
                          {children}
                        </table>
                      </div>
                    ),
                    thead: ({ children }) => (
                      <thead className="bg-gray-50">{children}</thead>
                    ),
                    tbody: ({ children }) => <tbody>{children}</tbody>,
                    tr: ({ children }) => (
                      <tr className="border-b border-gray-200 hover:bg-gray-50">
                        {children}
                      </tr>
                    ),
                    th: ({ children }) => (
                      <th className="border border-gray-300 px-3 py-2 text-left font-semibold text-gray-900 bg-gray-50">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="border border-gray-300 px-3 py-2 text-gray-700">
                        {children}
                      </td>
                    ),
                  }}
                >
                  {message.content || " "}
                </ReactMarkdown>
              </div>
            </div>

            <div className="text-xs text-gray-500 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
              {formatTime(message.timestamp)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
