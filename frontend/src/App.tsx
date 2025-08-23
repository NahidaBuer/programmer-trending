import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Chat from "./pages/Chat";

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
    </Router>
  );
}

export default App;
