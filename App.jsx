import React, { useState, useCallback } from "react";
import Sidebar from "./components/Sidebar.jsx";
import Topbar from "./components/Topbar.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import RecommendationsPage from "./pages/RecommendationsPage.jsx";
import Toast from "./components/Toast.jsx";
import "./styles/layout.css";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [toast, setToast] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const notify = useCallback((message, tone = "info") => {
    setToast({ message, tone, id: Date.now() });
  }, []);

  const bumpRefresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  return (
    <div className="app-shell">
      <Sidebar activeTab={activeTab} onSelect={setActiveTab} />
      <div className="app-main">
        <Topbar activeTab={activeTab} onScanComplete={notify} onDataChanged={bumpRefresh} />
        <div className="app-content">
          {activeTab === "dashboard" && (
            <DashboardPage refreshKey={refreshKey} notify={notify} onDataChanged={bumpRefresh} />
          )}
          {activeTab === "recommendations" && (
            <RecommendationsPage refreshKey={refreshKey} notify={notify} onDataChanged={bumpRefresh} />
          )}
        </div>
      </div>
      {toast && <Toast toast={toast} onDone={() => setToast(null)} />}
    </div>
  );
}
