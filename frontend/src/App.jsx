import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "./api";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import ViewHostels from "./pages/ViewHostels";
import Apply from "./pages/Apply";
import Status from "./pages/Status";
import Settings from "./pages/Settings";

function PrivateLayout({ authenticated, onLogout }) {
  if (!authenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>Dashboard</h2>
        <Navbar />
        <button className="logout" type="button" onClick={onLogout}>Logout</button>
      </aside>
      <main className="content">
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/home" element={<Home />} />
          <Route path="/hostels" element={<ViewHostels />} />
          <Route path="/apply" element={<Apply />} />
          <Route path="/status" element={<Status />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  const navigate = useNavigate();
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  async function refreshSession() {
    try {
      const res = await api.session();
      setAuthenticated(Boolean(res.authenticated));
    } catch {
      setAuthenticated(false);
    }
  }

  useEffect(() => {
    refreshSession().finally(() => setLoading(false));
  }, []);

  async function handleLogout() {
    await api.logout();
    setAuthenticated(false);
    navigate("/");
  }

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <Routes>
      <Route path="/" element={<Login onLogin={refreshSession} />} />
      <Route path="/register" element={<Register onRegister={refreshSession} />} />

      {/* Support old /static URLs during dev so login/register always appears. */}
      <Route path="/static" element={<Navigate to="/" replace />} />
      <Route path="/static/" element={<Navigate to="/" replace />} />
      <Route path="/static/register" element={<Navigate to="/register" replace />} />
      <Route path="/static/register/" element={<Navigate to="/register" replace />} />

      <Route path="/*" element={<PrivateLayout authenticated={authenticated} onLogout={handleLogout} />} />
    </Routes>
  );
}
