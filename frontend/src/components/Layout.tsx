import { Outlet } from "react-router-dom";
import Header from "./Header";

interface LayoutProps {
  activeSourceId?: string;
  onSourceChange: (sourceId: string) => void;
}

export default function Layout({
  activeSourceId,
  onSourceChange,
}: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 max-w-screen-lg mx-auto">
      <Header activeSourceId={activeSourceId} onSourceChange={onSourceChange} />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
