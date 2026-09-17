import React, { useState } from "react";
import { api } from "../api.js";

const COPY = {
  dashboard: {
    title: "Ürün Paneli",
    subtitle: "Maliyet, taban fiyat, mevcut fiyat ve piyasa fiyatını tek ekranda karşılaştırın.",
  },
  recommendations: {
    title: "Fiyat Önerileri ve Bildirimler",
    subtitle: "Sadece piyasası yükselmiş ve aksiyon gerektiren ürünler burada listelenir.",
  },
};

export default function Topbar({ activeTab, onScanComplete, onDataChanged }) {
  const [scanning, setScanning] = useState(false);
  const copy = COPY[activeTab] ?? COPY.dashboard;

  const handleScanAll = async () => {
    setScanning(true);
    try {
      const result = await api.scanAll();
      onDataChanged();
      onScanComplete(
        `Tarama tamamlandı: ${result.scanned_count} ürün kontrol edildi, ${result.action_needed_count} tanesi aksiyon bekliyor.`,
        result.action_needed_count > 0 ? "amber" : "guard"
      );
    } catch (err) {
      onScanComplete(err.message || "Tarama sırasında bir hata oluştu.", "error");
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="topbar">
      <div>
        <div className="topbar-title">{copy.title}</div>
        <div className="topbar-subtitle">{copy.subtitle}</div>
      </div>
      <button className="btn btn-guard" onClick={handleScanAll} disabled={scanning}>
        {scanning ? "Piyasa taranıyor…" : "Tüm Piyasayı Tara"}
      </button>
    </div>
  );
}
