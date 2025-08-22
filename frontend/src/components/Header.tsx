import { Link, useLocation } from "react-router-dom";
import SourceTabs from "./SourceTabs";

interface HeaderProps {
  activeSourceId?: string;
  onSourceChange: (sourceId: string) => void;
}

export default function Header({
  activeSourceId,
  onSourceChange,
}: HeaderProps) {
  const location = useLocation();
  const isHomePage = location.pathname === "/";

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* 左侧：标题和数据源切换 */}
          <div className="flex items-center space-x-6">
            <Link
              to="/"
              className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors"
            >
              Home
            </Link>
            {isHomePage && (
              <SourceTabs
                activeSourceId={activeSourceId}
                onSourceChange={onSourceChange}
              />
            )}
          </div>

          {/* 右侧：Chat 按钮 */}
          <div className="flex items-center space-x-4">
            <Link
              to="/chat"
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                location.pathname === "/chat"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              AI 对话
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
