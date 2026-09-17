import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Sidebar({ activeTab, onSelect }) {
  const [recCount, setRecCount] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const recs = await api.listRecommendations();
        if (!cancelled) setRecCount(recs.length);
      } catch (_) {
        /* sidebar sayaç hatasi sessizce yutulur, sayfa kendi hatasini gosterir */
      }
    };
    load();
    const interval = setInterval(load, 15000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [activeTab]);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">
          <span className="dot" />
          Fiyat Nöbeti
        </div>
        <div className="sidebar-brand-sub">v1.0 · yarı-otonom</div>
      </div>

      <nav className="sidebar-nav">
        <button
          className={`sidebar-nav-item ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => onSelect("dashboard")}
        >
          Ürün Paneli
        </button>
        <button
          className={`sidebar-nav-item ${activeTab === "recommendations" ? "active" : ""}`}
          onClick={() => onSelect("recommendations")}
        >
          Fiyat Önerileri
          {recCount > 0 && <span className="sidebar-nav-badge">{recCount}</span>}
        </button>
      </nav>

      <div className="sidebar-footer">
        Bu sistem fiyatları hiçbir platformda otomatik değiştirmez.
        Her değişiklik sizin onayınızla uygulanır.
      </div>
    </aside>
  );
}
