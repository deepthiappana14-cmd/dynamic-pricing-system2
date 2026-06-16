import { useCallback, useEffect, useState } from "react";
import { api } from "./api";

const SESSION_KEY = "dynamic_pricing_session";

function formatMoney(amount, currency = "USD") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(amount);
}

function DashboardView({ dashboard, onRefresh }) {
  const [name, setName] = useState("");
  const [sessionId, setSessionId] = useState(
    () => localStorage.getItem(SESSION_KEY) || "",
  );
  const [users, setUsers] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const loadUsers = useCallback(async () => {
    const data = await api.listUsers();
    setUsers(data);
  }, []);

  useEffect(() => {
    loadUsers().catch((err) => setError(err.message));
  }, [loadUsers, dashboard]);

  async function handleJoin(event) {
    event.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    setError("");
    try {
      const user = await api.joinUser(name.trim());
      localStorage.setItem(SESSION_KEY, user.session_id);
      setSessionId(user.session_id);
      setName("");
      await Promise.all([loadUsers(), onRefresh()]);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleLeave() {
    if (!sessionId) return;
    setBusy(true);
    setError("");
    try {
      await api.leaveUser(sessionId);
      localStorage.removeItem(SESSION_KEY);
      setSessionId("");
      await Promise.all([loadUsers(), onRefresh()]);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const price = dashboard.current_price;

  return (
    <div className="grid" style={{ gap: "1rem" }}>
      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-3">
        <div className="card">
          <div className="stat-label">Active users</div>
          <div className="stat-value">{dashboard.active_users}</div>
        </div>
        <div className="card">
          <div className="stat-label">Total sessions</div>
          <div className="stat-value">{dashboard.total_users}</div>
        </div>
        <div className="card">
          <div className="stat-label">Pricing mode</div>
          <div className="stat-value" style={{ fontSize: "1.5rem" }}>
            {dashboard.config.mode}
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem" }}>
          <div>
            <span className="badge success">Live price</span>
            <div className="price-display">
              {formatMoney(price.price, price.currency)}
              <span style={{ fontSize: "1rem", color: "var(--muted)" }}>/mo</span>
            </div>
            <div className="price-breakdown">{price.breakdown}</div>
          </div>
          {price.tier_label && <span className="badge">{price.tier_label}</span>}
        </div>
      </div>

      <div className="card">
        <h2>Simulate active users</h2>
        <p style={{ color: "var(--muted)", marginTop: 0 }}>
          Join or leave the service to change the active user count and watch the price update in real time.
        </p>
        <form className="form-row" onSubmit={handleJoin}>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter a display name"
            disabled={busy || Boolean(sessionId)}
          />
          <button className="btn btn-primary" type="submit" disabled={busy || Boolean(sessionId)}>
            Join service
          </button>
          {sessionId && (
            <button className="btn btn-secondary" type="button" onClick={handleLeave} disabled={busy}>
              Leave service
            </button>
          )}
        </form>
      </div>

      <div className="card">
        <h2>User sessions</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Session</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={4} className="empty">
                    No users yet. Join the service to start the simulation.
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.session_id}>
                    <td>{user.display_name}</td>
                    <td>
                      <span className={`badge ${user.is_active ? "success" : ""}`}>
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="mono">{user.session_id.slice(0, 8)}…</td>
                    <td>{new Date(user.joined_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function AdminView({ config, onRefresh }) {
  const [form, setForm] = useState({
    mode: config.mode,
    base_price: config.base_price,
    per_user_rate: config.per_user_rate,
    currency: config.currency,
  });
  const [tierForm, setTierForm] = useState({
    min_users: 0,
    max_users: 50,
    price: 9.99,
    label: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setForm({
      mode: config.mode,
      base_price: config.base_price,
      per_user_rate: config.per_user_rate,
      currency: config.currency,
    });
  }, [config]);

  async function saveConfig(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.updateConfig({
        mode: form.mode,
        base_price: Number(form.base_price),
        per_user_rate: Number(form.per_user_rate),
        currency: form.currency,
      });
      await onRefresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function addTier(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.createTier({
        min_users: Number(tierForm.min_users),
        max_users: tierForm.max_users === "" ? null : Number(tierForm.max_users),
        price: Number(tierForm.price),
        label: tierForm.label,
      });
      setTierForm({ min_users: 0, max_users: 50, price: 9.99, label: "" });
      await onRefresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function removeTier(id) {
    setBusy(true);
    setError("");
    try {
      await api.deleteTier(id);
      await onRefresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid" style={{ gap: "1rem" }}>
      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <h2>Pricing configuration</h2>
        <form onSubmit={saveConfig}>
          <div className="form-row">
            <select
              value={form.mode}
              onChange={(e) => setForm({ ...form, mode: e.target.value })}
            >
              <option value="tiered">Tiered pricing</option>
              <option value="linear">Linear pricing</option>
            </select>
            <input
              value={form.currency}
              onChange={(e) => setForm({ ...form, currency: e.target.value.toUpperCase() })}
              placeholder="Currency"
              maxLength={3}
            />
          </div>
          <div className="form-row">
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.base_price}
              onChange={(e) => setForm({ ...form, base_price: e.target.value })}
              placeholder="Base price (linear mode)"
            />
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.per_user_rate}
              onChange={(e) => setForm({ ...form, per_user_rate: e.target.value })}
              placeholder="Per-user rate (linear mode)"
            />
            <button className="btn btn-primary" type="submit" disabled={busy}>
              Save config
            </button>
          </div>
        </form>
        <p style={{ color: "var(--muted)", marginBottom: 0 }}>
          Use <strong>tiered</strong> mode with the tiers below, or switch to <strong>linear</strong> mode
          where price = base + (active users × rate).
        </p>
      </div>

      <div className="card">
        <h2>Pricing tiers</h2>
        <div className="tier-list">
          {config.tiers.map((tier) => (
            <div className="tier-item" key={tier.id}>
              <div>
                <strong>{tier.label || "Untitled tier"}</strong>
                <div className="mono" style={{ color: "var(--muted)" }}>
                  {tier.min_users} – {tier.max_users ?? "∞"} users
                </div>
              </div>
              <div>{formatMoney(tier.price, config.currency)}/mo</div>
              <div className="mono">ID {tier.id}</div>
              <button
                className="btn btn-danger"
                type="button"
                onClick={() => removeTier(tier.id)}
                disabled={busy}
              >
                Delete
              </button>
            </div>
          ))}
        </div>

        <form onSubmit={addTier} style={{ marginTop: "1rem" }}>
          <div className="form-row">
            <input
              type="number"
              min="0"
              value={tierForm.min_users}
              onChange={(e) => setTierForm({ ...tierForm, min_users: e.target.value })}
              placeholder="Min users"
            />
            <input
              type="number"
              min="0"
              value={tierForm.max_users}
              onChange={(e) => setTierForm({ ...tierForm, max_users: e.target.value })}
              placeholder="Max users (blank = unlimited)"
            />
            <input
              type="number"
              step="0.01"
              min="0"
              value={tierForm.price}
              onChange={(e) => setTierForm({ ...tierForm, price: e.target.value })}
              placeholder="Price"
            />
            <input
              value={tierForm.label}
              onChange={(e) => setTierForm({ ...tierForm, label: e.target.value })}
              placeholder="Label"
            />
            <button className="btn btn-secondary" type="submit" disabled={busy}>
              Add tier
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState("dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const data = await api.getDashboard();
    setDashboard(data);
  }, []);

  useEffect(() => {
    refresh()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));

    const interval = setInterval(() => {
      refresh().catch(() => {});
    }, 5000);

    return () => clearInterval(interval);
  }, [refresh]);

  if (loading) {
    return (
      <div className="app-shell">
        <p>Loading dynamic pricing dashboard…</p>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="app-shell">
        <div className="error-banner">
          {error || "Unable to load dashboard. Is the backend running on port 8000?"}
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <h1>Dynamic Pricing System</h1>
          <p>
            A database-driven demo that adjusts monthly service pricing based on the number of
            active users. Built with FastAPI, SQLite, and React.
          </p>
        </div>
        <span className="badge">Engineering student project</span>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${tab === "dashboard" ? "active" : ""}`}
          onClick={() => setTab("dashboard")}
        >
          Live dashboard
        </button>
        <button
          className={`tab ${tab === "admin" ? "active" : ""}`}
          onClick={() => setTab("admin")}
        >
          Admin config
        </button>
      </nav>

      {tab === "dashboard" ? (
        <DashboardView dashboard={dashboard} onRefresh={refresh} />
      ) : (
        <AdminView config={dashboard.config} onRefresh={refresh} />
      )}
    </div>
  );
}
