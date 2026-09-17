const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let detail = `İstek başarısız oldu (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch (_) {
      /* yanıt boş olabilir */
    }
    throw new Error(detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  listProducts: () => request("/products"),
  createProduct: (payload) =>
    request("/products", { method: "POST", body: JSON.stringify(payload) }),
  updateProduct: (id, payload) =>
    request(`/products/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteProduct: (id) => request(`/products/${id}`, { method: "DELETE" }),
  scanProduct: (id) => request(`/products/${id}/scan`, { method: "POST" }),
  scanAll: () => request("/scan-all", { method: "POST" }),
  listRecommendations: () => request("/recommendations"),
  applyRecommendation: (id, newPrice) =>
    request(`/products/${id}/apply-recommendation`, {
      method: "POST",
      body: JSON.stringify(newPrice != null ? { new_price: newPrice } : {}),
    }),
  dismissRecommendation: (id) =>
    request(`/products/${id}/dismiss-recommendation`, { method: "POST" }),
};
