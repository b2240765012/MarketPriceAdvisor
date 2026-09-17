import React, { useEffect, useState, useCallback } from "react";
import { api } from "../api.js";
import PriceRibbon from "../components/PriceRibbon.jsx";
import ProductFormModal from "../components/ProductFormModal.jsx";
import "../styles/table.css";

export default function DashboardPage({ refreshKey, notify, onDataChanged }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listProducts();
      setProducts(data);
      setError(null);
    } catch (err) {
      setError(err.message || "Ürünler yüklenemedi.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load, refreshKey]);

  const handleCreate = async (payload) => {
    await api.createProduct(payload);
    setShowForm(false);
    notify(`${payload.product_name} eklendi. Taban fiyat sistemin kar korumasını devreye aldı.`, "guard");
    onDataChanged();
  };

  const handleScan = async (product) => {
    setBusyId(product.id);
    try {
      const updated = await api.scanProduct(product.id);
      onDataChanged();
      if (updated.action_needed) {
        notify(`${updated.product_name}: piyasa yükseldi, yeni öneri hazır.`, "amber");
      } else {
        notify(`${updated.product_name} için piyasa tarandı.`, "guard");
      }
    } catch (err) {
      notify(err.message || "Tarama başarısız oldu.", "error");
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (product) => {
    if (!window.confirm(`${product.product_name} silinsin mi?`)) return;
    setBusyId(product.id);
    try {
      await api.deleteProduct(product.id);
      notify(`${product.product_name} silindi.`, "info");
      onDataChanged();
    } catch (err) {
      notify(err.message || "Silme işlemi başarısız oldu.", "error");
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div>
      <div className="section-toolbar">
        <div className="stat-strip">
          <Stat label="Ürün" value={products.length} />
          <Stat
            label="Aksiyon Bekleyen"
            value={products.filter((p) => p.action_needed).length}
            tone="amber"
          />
          <Stat
            label="Marjı Korunan"
            value={products.filter((p) => !p.action_needed).length}
            tone="guard"
          />
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          + Yeni Ürün Ekle
        </button>
      </div>

      {loading && <div className="empty-state">Yükleniyor…</div>}
      {!loading && error && <div className="empty-state empty-state-error">{error}</div>}

      {!loading && !error && products.length === 0 && (
        <div className="empty-state">
          Henüz ürün eklenmedi. Piyasa takibine başlamak için bir ürün ekleyin.
        </div>
      )}

      {!loading && !error && products.length > 0 && (
        <div className="table-wrap">
          <table className="product-table">
            <thead>
              <tr>
                <th>Ürün</th>
                <th>Maliyet</th>
                <th>Kâr %</th>
                <th>Fiyat Karşılaştırması</th>
                <th>Durum</th>
                <th>Son Tarama</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>
                    <div className="cell-title">{p.product_name}</div>
                    <div className="cell-sub mono">{p.sku}</div>
                  </td>
                  <td className="mono">{p.cost.toFixed(2)} TL</td>
                  <td className="mono">%{p.min_profit_rate}</td>
                  <td>
                    <PriceRibbon
                      basePrice={p.base_price}
                      currentPrice={p.current_price}
                      marketPrice={p.market_price}
                      recommendedPrice={p.recommended_price}
                    />
                  </td>
                  <td>
                    <StatusPill product={p} />
                  </td>
                  <td className="cell-sub">
                    {p.last_scanned_at
                      ? new Date(p.last_scanned_at).toLocaleString("tr-TR")
                      : "Taranmadı"}
                  </td>
                  <td className="cell-actions">
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => handleScan(p)}
                      disabled={busyId === p.id}
                    >
                      Tara
                    </button>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => handleDelete(p)}
                      disabled={busyId === p.id}
                    >
                      Sil
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <ProductFormModal onClose={() => setShowForm(false)} onSubmit={handleCreate} />
      )}
    </div>
  );
}

function Stat({ label, value, tone }) {
  return (
    <div className={`stat-card ${tone ? `stat-card-${tone}` : ""}`}>
      <div className="stat-value mono">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function StatusPill({ product }) {
  if (product.action_needed) {
    return <span className="pill pill-amber">Aksiyon gerekli</span>;
  }
  if (!product.market_price) {
    return <span className="pill pill-neutral">Taranmadı</span>;
  }
  return <span className="pill pill-guard">Marj korunuyor</span>;
}
