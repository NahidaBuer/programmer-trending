import { useEffect } from "react";
import { useSources } from "../hooks/useSWR";

interface SourceTabsProps {
  activeSourceId?: string;
  onSourceChange: (sourceId: string) => void;
}

export default function SourceTabs({
  activeSourceId,
  onSourceChange,
}: SourceTabsProps) {
  const { sources, loading, error } = useSources();

  // 如果没有选中的数据源，默认选择第一个
  useEffect(() => {
    if (!activeSourceId && sources && sources.length > 0) {
      onSourceChange(sources[0].id);
    }
  }, [activeSourceId, sources, onSourceChange]);

  if (loading) {
    return (
      <div className="flex space-x-4">
        <div className="h-10 w-24 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-10 w-24 bg-gray-200 rounded animate-pulse"></div>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-600 text-sm">加载数据源失败</div>;
  }

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
      {sources.map((source) => (
        <button
          key={source.id}
          onClick={() => onSourceChange(source.id)}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeSourceId === source.id
              ? "bg-white text-blue-600 shadow-sm"
              : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
          }`}
        >
          {source.name}
        </button>
      ))}
    </div>
  );
}
