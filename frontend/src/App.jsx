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
import AdminDashboard from "./pages/AdminDashboard";
import AdminActivity from "./pages/AdminActivity";

function PrivateLayout({ authenticated, currentUser, onLogout, onToast }) {
  if (!authenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>Dashboard</h2>
        <Navbar currentUser={currentUser} />
        <button className="logout" type="button" onClick={onLogout}>Logout</button>
      </aside>
      <main className="content">
        <Routes>
          <Route
            path="/dashboard"
            element={currentUser?.is_admin ? <AdminDashboard onToast={onToast} /> : <Dashboard onToast={onToast} />}
          />
          <Route
            path="/admin-dashboard"
            element={
              currentUser?.is_admin ? (
                <AdminDashboard onToast={onToast} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            }
          />
          <Route
            path="/admin-activity"
            element={
              currentUser?.is_admin ? (
                <AdminActivity onToast={onToast} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            }
          />
          <Route path="/home" element={<Home />} />
          <Route path="/hostels" element={<ViewHostels />} />
          <Route path="/apply" element={<Apply onToast={onToast} />} />
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
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  function showToast(message, type = "success") {
    setToast({ message, type });
    window.clearTimeout(window.__toastTimer);
    window.__toastTimer = window.setTimeout(() => setToast(null), 2500);
  }

  async function refreshSession() {
    try {
      const res = await api.session();
      setAuthenticated(Boolean(res.authenticated));
      setCurrentUser(res.user || null);
      return Boolean(res.authenticated);
    } catch {
      setAuthenticated(false);
      setCurrentUser(null);
      return false;
    }
  }

  useEffect(() => {
    refreshSession().finally(() => setLoading(false));
  }, []);

  async function handleLogout() {
    await api.logout();
    setAuthenticated(false);
    setCurrentUser(null);
    showToast("Logged out successfully", "success");
    navigate("/");
  }

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <>
      {toast && <div className={`toast ${toast.type}`}>{toast.message}</div>}
      <Routes>
        <Route path="/" element={<Login onLogin={refreshSession} onToast={showToast} />} />
        <Route path="/register" element={<Register onRegister={refreshSession} onToast={showToast} />} />

        {/* Support old /static URLs during dev so login/register always appears. */}
        <Route path="/static" element={<Navigate to="/" replace />} />
        <Route path="/static/" element={<Navigate to="/" replace />} />
        <Route path="/static/register" element={<Navigate to="/register" replace />} />
        <Route path="/static/register/" element={<Navigate to="/register" replace />} />

        <Route
          path="/*"
          element={
            <PrivateLayout
              authenticated={authenticated}
              currentUser={currentUser}
              onLogout={handleLogout}
              onToast={showToast}
            />
          }
        />
      </Routes>
    </>
  );
}
