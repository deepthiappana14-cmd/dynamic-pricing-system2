const API_BASE = "https://dynamic-pricing-system2.onrender.com/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || "Request failed");
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  getDashboard: () => request("/dashboard"),
  getPrice: () => request("/price"),
  listUsers: () => request("/users"),
  joinUser: (displayName) =>
    request("/users", {
      method: "POST",
      body: JSON.stringify({ display_name: displayName }),
    }),
  leaveUser: (sessionId) =>
    request(`/users/${sessionId}/leave`, { method: "POST" }),
  removeUser: (sessionId) =>
    request(`/users/${sessionId}`, { method: "DELETE" }),
  getConfig: () => request("/admin/config"),
  updateConfig: (payload) =>
    request("/admin/config", {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  createTier: (payload) =>
    request("/admin/tiers", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateTier: (id, payload) =>
    request(`/admin/tiers/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteTier: (id) =>
    request(`/admin/tiers/${id}`, { method: "DELETE" }),
};
