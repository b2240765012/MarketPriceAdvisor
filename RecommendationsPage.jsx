import React, { useEffect, useState, useCallback } from "react";
import { api } from "../api.js";
import PriceRibbon from "../components/PriceRibbon.jsx";
import "../styles/recommendations.css";

export default function RecommendationsPage({ refreshKey, notify, onDataChanged }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listRecommendations();
      setItems(data);
      setError(null);
    } catch (err) {
      setError(err.message || "Öneriler yüklenemedi.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load, refreshKey]);

  const handleApply = async (product) => {
    setBusyId(product.id);
    try {
      const updated = await api.applyRecommendation(product.id, null);
      notify(
        `${updated.product_name} fiyatı ${updated.current_price.toFixed(2)} TL olarak güncellendi.`,
        "guard"
      );
      setItems((prev) => prev.filter((p) => p.id !== product.id));
      onDataChanged();
    } catch (err) {
      notify(err.message || "Fiyat güncellenemedi.", "error");
    } finally {
      setBusyId(null);
    }
  };

  const handleDismiss = async (product) => {
    setBusyId(product.id);
    try {
      await api.dismissRecommendation(product.id);
      setItems((prev) => prev.filter((p) => p.id !== product.id));
      onDataChanged();
    } catch (err) {
      notify(err.message || "İşlem başarısız oldu.", "error");
    } finally {
      setBusyId(null);
    }
  };

  if (loading) return <div className="empty-state">Yükleniyor…</div>;
  if (error) return <div className="empty-state empty-state-error">{error}</div>;

  if (items.length === 0) {
    return (
      <div className="empty-state">
        Şu an aksiyon bekleyen bir öneri yok. Piyasa yükseldiğinde ürünler burada listelenecek.
      </div>
    );
  }

  return (
    <div className="rec-grid">
      {items.map((p) => (
        <div className="rec-card" key={p.id}>
          <div className="rec-card-head">
            <div>
              <div className="rec-card-title">{p.product_name}</div>
              <div className="cell-sub mono">{p.sku}</div>
            </div>
            <span className="pill pill-amber">Piyasa yükseldi</span>
          </div>

          <p className="rec-card-message">{p.reason}</p>

          <PriceRibbon
            basePrice={p.base_price}
            currentPrice={p.current_price}
            marketPrice={p.market_price}
            recommendedPrice={p.recommended_price}
          />

          <div className="rec-card-numbers">
            <div>
              <span className="cell-sub">Mevcut Fiyat</span>
              <div className="mono rec-number">{p.current_price.toFixed(2)} TL</div>
            </div>
            <div className="rec-arrow">→</div>
            <div>
              <span className="cell-sub">Önerilen Fiyat</span>
              <div className="mono rec-number rec-number-highlight">
                {p.recommended_price?.toFixed(2)} TL
              </div>
            </div>
          </div>

          <div className="rec-card-actions">
            <button className="btn btn-ghost" onClick={() => handleDismiss(p)} disabled={busyId === p.id}>
              Şimdi Değil
            </button>
            <button className="btn btn-guard" onClick={() => handleApply(p)} disabled={busyId === p.id}>
              {busyId === p.id ? "Uygulanıyor…" : "Önerilen Fiyatı Uygula"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
