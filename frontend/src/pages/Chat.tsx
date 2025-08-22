export default function Chat() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center py-16">
        <div className="mb-8">
          <svg 
            className="w-16 h-16 mx-auto text-gray-400" 
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
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-4">AI 对话助手</h1>
        <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
          与 AI 助手对话，讨论技术话题、获取编程建议，或基于热榜文章进行深入探讨。
        </p>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-md mx-auto">
          <div className="flex items-center mb-3">
            <svg className="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <span className="font-medium text-blue-900">开发中</span>
          </div>
          <p className="text-blue-800 text-sm">
            AI 对话功能正在开发中，敬请期待！我们将集成 Google Gemini AI，为您提供智能的技术讨论和问答服务。
          </p>
        </div>

        <div className="mt-8">
          <button
            onClick={() => window.history.back()}
            className="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors"
          >
            返回首页
          </button>
        </div>
      </div>
    </div>
  );
}