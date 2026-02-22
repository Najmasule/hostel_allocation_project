import { useEffect, useMemo, useState } from "react";
import { api } from "../api";

export default function AdminActivity({ onToast }) {
  const [activities, setActivities] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [action, setAction] = useState("all");

  useEffect(() => {
    api.adminDashboard()
      .then((res) => {
        setActivities(res.activities || []);
      })
      .catch((err) => {
        setError(err.message);
        onToast?.(err.message, "error");
      })
      .finally(() => setLoading(false));
  }, [onToast]);

  const filtered = useMemo(() => {
    return activities.filter((row) => {
      const q = query.trim().toLowerCase();
      const matchesAction = action === "all" ? true : row.action === action;
      if (!q) return matchesAction;
      const hay = `${row.user__username || ""} ${row.action || ""} ${row.details || ""}`.toLowerCase();
      return matchesAction && hay.includes(q);
    });
  }, [activities, query, action]);

  if (loading) {
    return (
      <section className="section">
        <h1 className="main-title">Admin Activity Dashboard</h1>
        <p className="subtitle">Loading...</p>
      </section>
    );
  }

  return (
    <section className="section">
      <h1 className="main-title">Admin Activity Dashboard</h1>
      <p className="subtitle">Kila kilichofanywa na users kinaonekana hapa.</p>
      {error && <p className="error">{error}</p>}

      <div className="actions-row">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by user/action/details"
        />
        <select value={action} onChange={(e) => setAction(e.target.value)}>
          <option value="all">All actions</option>
          <option value="register">register</option>
          <option value="login">login</option>
          <option value="logout">logout</option>
          <option value="apply">apply</option>
          <option value="allocate">allocate</option>
        </select>
      </div>

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Action</th>
              <th>Details</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan="5">No activity found.</td></tr>
            ) : (
              filtered.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row.user__username || "unknown"}</td>
                  <td>{row.action}</td>
                  <td>{row.details || "-"}</td>
                  <td>{new Date(row.created_at).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
