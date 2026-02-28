import { useEffect, useMemo, useState } from "react";
import { api } from "../api";

export default function AdminDashboard({ onToast }) {
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [activities, setActivities] = useState([]);
  const [roomEdits, setRoomEdits] = useState({});
  const [pendingDeleteUserId, setPendingDeleteUserId] = useState(null);
  const [pendingRoomAllocationId, setPendingRoomAllocationId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const studentUserIds = useMemo(() => {
    return new Set(
      allocations
        .map((a) => users.find((u) => u.username === a.student__username)?.id)
        .filter((id) => typeof id === "number")
    );
  }, [allocations, users]);

  async function loadAdminData() {
    const res = await api.adminDashboard();
    setSummary(res.summary || {});
    setUsers(res.users || []);
    setAllocations(res.allocations || []);
    setActivities(res.activities || []);

    setRoomEdits((prev) => {
      const next = { ...prev };
      for (const item of res.allocations || []) {
        if (next[item.id] === undefined) {
          next[item.id] = item.room_number || "";
        }
      }
      return next;
    });
  }

  useEffect(() => {
    loadAdminData()
      .catch((err) => {
        setError(err.message);
        onToast?.(err.message, "error");
      })
      .finally(() => setLoading(false));
  }, [onToast]);

  async function handleDeleteUser(user) {
    const confirmed = window.confirm(`Delete user ${user.username}? This will also remove their allocation.`);
    if (!confirmed) return;

    setPendingDeleteUserId(user.id);
    setError("");
    try {
      const res = await api.adminDeleteUser(user.id);
      onToast?.(res.message || "User deleted", "success");
      await loadAdminData();
    } catch (err) {
      setError(err.message);
      onToast?.(err.message, "error");
    } finally {
      setPendingDeleteUserId(null);
    }
  }

  async function handleUpdateRoom(allocation) {
    const roomNumber = (roomEdits[allocation.id] ?? "").trim();
    if (!roomNumber) {
      onToast?.("Weka room number kwanza", "error");
      return;
    }

    setPendingRoomAllocationId(allocation.id);
    setError("");
    try {
      const res = await api.adminUpdateRoom(allocation.id, roomNumber);
      onToast?.(res.message || "Room updated", "success");
      await loadAdminData();
    } catch (err) {
      setError(err.message);
      onToast?.(err.message, "error");
    } finally {
      setPendingRoomAllocationId(null);
    }
  }

  if (loading) {
    return (
      <section className="section">
        <h1 className="main-title">Admin Dashboard</h1>
        <p className="subtitle">Loading...</p>
      </section>
    );
  }

  return (
    <section className="section">
      <h1 className="main-title">Admin Dashboard</h1>
      <p className="subtitle">Ufuatiliaji wa shughuli zote za users.</p>
      {error && <p className="error">{error}</p>}

      <div className="cards stats-cards">
        <div className="card"><h3>Users</h3><p>{summary?.total_users || 0}</p></div>
        <div className="card"><h3>Students</h3><p>{summary?.total_students || 0}</p></div>
        <div className="card"><h3>Hostels</h3><p>{summary?.total_hostels || 0}</p></div>
        <div className="card"><h3>Allocations</h3><p>{summary?.total_allocations || 0}</p></div>
        <div className="card"><h3>Activities</h3><p>{summary?.total_activities || 0}</p></div>
      </div>

      <h2>Users</h2>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Name</th>
              <th>Role</th>
              <th>Staff</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr><td colSpan="6">No users found.</td></tr>
            ) : (
              users.map((u) => {
                const canDelete = u.role === "student" || studentUserIds.has(u.id);
                return (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td>{u.username}</td>
                    <td>{u.first_name || "-"}</td>
                    <td>{u.role || "-"}</td>
                    <td>{u.is_staff ? "Yes" : "No"}</td>
                    <td>
                      <button
                        type="button"
                        disabled={!canDelete || pendingDeleteUserId === u.id}
                        onClick={() => handleDeleteUser(u)}
                      >
                        {pendingDeleteUserId === u.id ? "Deleting..." : "Delete"}
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <h2>Allocations</h2>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student</th>
              <th>Hostel</th>
              <th>Room</th>
              <th>Allocated On</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {allocations.length === 0 ? (
              <tr><td colSpan="6">No allocations found.</td></tr>
            ) : (
              allocations.map((a) => (
                <tr key={a.id}>
                  <td>{a.id}</td>
                  <td>{a.student__username}</td>
                  <td>{a.hostel__name}</td>
                  <td>
                    <input
                      type="text"
                      value={roomEdits[a.id] ?? ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setRoomEdits((prev) => ({ ...prev, [a.id]: value }));
                      }}
                      placeholder="Room no"
                    />
                  </td>
                  <td>{new Date(a.allocated_on).toLocaleString()}</td>
                  <td>
                    <button
                      type="button"
                      disabled={pendingRoomAllocationId === a.id}
                      onClick={() => handleUpdateRoom(a)}
                    >
                      {pendingRoomAllocationId === a.id ? "Saving..." : "Save room"}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <h2>Recent Activities</h2>
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
            {activities.length === 0 ? (
              <tr><td colSpan="5">No activities found.</td></tr>
            ) : (
              activities.map((act) => (
                <tr key={act.id}>
                  <td>{act.id}</td>
                  <td>{act.user__username || "unknown"}</td>
                  <td>{act.action}</td>
                  <td>{act.details || "-"}</td>
                  <td>{new Date(act.created_at).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
