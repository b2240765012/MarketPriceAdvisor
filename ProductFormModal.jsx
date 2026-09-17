import React, { useState } from "react";
import "../styles/modal.css";

const emptyForm = {
  sku: "",
  product_name: "",
  cost: "",
  min_profit_rate: "",
  current_price: "",
  competitor_url: "",
};

export default function ProductFormModal({ onClose, onSubmit }) {
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const basePreview =
    form.cost && form.min_profit_rate
      ? (parseFloat(form.cost) * (1 + parseFloat(form.min_profit_rate) / 100)).toFixed(2)
      : null;

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit({
        sku: form.sku.trim(),
        product_name: form.product_name.trim(),
        cost: parseFloat(form.cost),
        min_profit_rate: parseFloat(form.min_profit_rate),
        current_price: parseFloat(form.current_price),
        competitor_url: form.competitor_url.trim() || null,
      });
    } catch (err) {
      setError(err.message || "Ürün eklenirken bir hata oluştu.");
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-panel">
        <div className="modal-header">
          <h2>Yeni Ürün Ekle</h2>
          <button className="btn btn-ghost btn-sm" onClick={onClose} aria-label="Kapat">
            Kapat
          </button>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <label>
              Ürün Adı
              <input required value={form.product_name} onChange={handleChange("product_name")} placeholder="Kablosuz Kulaklık" />
            </label>
            <label>
              SKU / Barkod
              <input required value={form.sku} onChange={handleChange("sku")} placeholder="SKU-0231" />
            </label>
          </div>

          <div className="form-row">
            <label>
              Maliyet (TL)
              <input required type="number" step="0.01" min="0.01" value={form.cost} onChange={handleChange("cost")} placeholder="100" />
            </label>
            <label>
              Minimum Kâr Oranı (%)
              <input required type="number" step="0.1" min="0" value={form.min_profit_rate} onChange={handleChange("min_profit_rate")} placeholder="10" />
            </label>
          </div>

          <div className="form-row">
            <label>
              Mevcut Satış Fiyatı (TL)
              <input required type="number" step="0.01" min="0.01" value={form.current_price} onChange={handleChange("current_price")} placeholder="115" />
            </label>
            <label>
              Rakip / Piyasa URL (opsiyonel)
              <input value={form.competitor_url} onChange={handleChange("competitor_url")} placeholder="https://..." />
            </label>
          </div>

          {basePreview && (
            <div className="form-hint">
              Bu ürün için taban fiyat <b className="mono">{basePreview} TL</b> olacak — sistem bu fiyatın altında hiçbir zaman öneri sunmayacak.
            </div>
          )}

          {error && <div className="form-error">{error}</div>}

          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose}>Vazgeç</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Ekleniyor…" : "Ürünü Ekle"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
