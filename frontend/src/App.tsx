import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import DiscussionCartButton from "./components/DiscussionCartButton";

function App() {
  const [activeSourceId, setActiveSourceId] = useState<string>();

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <Layout
              activeSourceId={activeSourceId}
              onSourceChange={setActiveSourceId}
            />
          }
        >
          <Route index element={<Home activeSourceId={activeSourceId} />} />
          <Route path="chat" element={<Chat />} />
        </Route>
      </Routes>
      
      {/* 全局悬浮按钮 */}
      <DiscussionCartButton />
    </Router>
  );
}

export default App;
