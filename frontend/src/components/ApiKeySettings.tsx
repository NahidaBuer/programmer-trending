import { useState, useEffect } from "react";

interface ApiKeySettingsProps {
  onApiKeyChange: (apiKey: string | null) => void;
}

export default function ApiKeySettings({
  onApiKeyChange,
}: ApiKeySettingsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [useOwnKey, setUseOwnKey] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);

  // 从 localStorage 恢复设置
  useEffect(() => {
    const savedUseOwnKey = localStorage.getItem("chat_use_own_key") === "true";
    const savedApiKey = localStorage.getItem("chat_api_key") || "";

    setUseOwnKey(savedUseOwnKey);
    setApiKey(savedApiKey);

    // 通知父组件
    if (savedUseOwnKey && savedApiKey) {
      onApiKeyChange(savedApiKey);
    } else {
      onApiKeyChange(null);
    }
  }, [onApiKeyChange]);

  const handleUseOwnKeyChange = (checked: boolean) => {
    setUseOwnKey(checked);
    localStorage.setItem("chat_use_own_key", checked.toString());

    if (checked && apiKey) {
      onApiKeyChange(apiKey);
    } else {
      onApiKeyChange(null);
    }
  };

  const handleApiKeyChange = (value: string) => {
    setApiKey(value);
    localStorage.setItem("chat_api_key", value);

    if (useOwnKey && value) {
      onApiKeyChange(value);
    }
  };

  const maskApiKey = (key: string) => {
    if (key.length <= 8) return key;
    return key.substring(0, 4) + "••••••••" + key.substring(key.length - 4);
  };

  return (
    <div className="relative">
      {/* 设置按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        title="API 设置"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </button>

      {/* 设置面板 */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <div className="p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              聊天设置
            </h3>

            {/* 模式选择 */}
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <input
                  type="radio"
                  id="anonymous"
                  name="chat_mode"
                  checked={!useOwnKey}
                  onChange={() => handleUseOwnKeyChange(false)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <label
                    htmlFor="anonymous"
                    className="block font-medium text-gray-900"
                  >
                    匿名模式 (推荐)
                  </label>
                  <p className="text-sm text-gray-600 mt-1">
                    使用服务器提供的 API，每10分钟最多5条消息
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <input
                  type="radio"
                  id="own_key"
                  name="chat_mode"
                  checked={useOwnKey}
                  onChange={() => handleUseOwnKeyChange(true)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <label
                    htmlFor="own_key"
                    className="block font-medium text-gray-900"
                  >
                    自定义 API Key
                  </label>
                  <p className="text-sm text-gray-600 mt-1">
                    使用你自己的 Google Gemini API Key，无限制
                  </p>
                </div>
              </div>
            </div>

            {/* API Key 输入 */}
            {useOwnKey && (
              <div className="mt-4 space-y-3">
                <label className="block text-sm font-medium text-gray-700">
                  Google Gemini API Key
                </label>
                <div className="relative">
                  <input
                    type={showKey ? "text" : "password"}
                    value={apiKey}
                    onChange={(e) => handleApiKeyChange(e.target.value)}
                    placeholder="输入你的 API Key..."
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showKey ? (
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
                        />
                      </svg>
                    ) : (
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                      </svg>
                    )}
                  </button>
                </div>

                {apiKey && (
                  <div className="text-sm text-green-600">
                    ✓ API Key 已保存: {maskApiKey(apiKey)}
                  </div>
                )}

                <div className="text-xs text-gray-500">
                  <p>• API Key 仅存储在本地浏览器中</p>
                  <p>
                    • 可在{" "}
                    <a
                      href="https://aistudio.google.com/app/apikey"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      Google AI Studio
                    </a>{" "}
                    获取免费 API Key
                  </p>
                </div>
              </div>
            )}

            {/* 关闭按钮 */}
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                完成
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 遮罩层 */}
      {isOpen && (
        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
      )}
    </div>
  );
}
