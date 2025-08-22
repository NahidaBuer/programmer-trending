import ItemList from "../components/ItemList";

interface HomeProps {
  activeSourceId?: string;
}

export default function Home({ activeSourceId }: HomeProps) {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Programmer Trending
        </h1>
        <p className="text-gray-600">
          聚合多个技术社区的热门内容，通过 AI 生成中文摘要，帮你快速了解技术趋势
        </p>
      </div>

      <ItemList sourceId={activeSourceId} />
    </div>
  );
}
