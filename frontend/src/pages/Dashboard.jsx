import { useEffect, useState } from "react";
import { api } from "../api";

export default function Dashboard() {
  const [hostels, setHostels] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.dashboard()
      .then((res) => {
        setHostels(res.hostels || []);
        setAllocations(res.allocations || []);
        setUser(res.user || null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <section className="section">
        <h1 className="main-title">Dashboard</h1>
        <p className="subtitle">Loading data...</p>
      </section>
    );
  }

  return (
    <section className="section">
      <h1 className="main-title">Dashboard</h1>
      {user && (
        <p className="subtitle">
          User: <strong>{user.name || user.username}</strong> ({user.role})
        </p>
      )}
      {error && <p className="error">{error}</p>}

      <h2>Hostels Table (Django)</h2>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Location</th>
              <th>Available Rooms</th>
            </tr>
          </thead>
          <tbody>
            {hostels.length === 0 ? (
              <tr>
                <td colSpan="4">No hostels found.</td>
              </tr>
            ) : (
              hostels.map((hostel) => (
                <tr key={hostel.id}>
                  <td>{hostel.id}</td>
                  <td>{hostel.name}</td>
                  <td>{hostel.location}</td>
                  <td>{hostel.total_rooms}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <h2>Allocations Table (Django)</h2>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student</th>
              <th>Hostel</th>
              <th>Room</th>
              <th>Allocated On</th>
            </tr>
          </thead>
          <tbody>
            {allocations.length === 0 ? (
              <tr>
                <td colSpan="5">No allocations found.</td>
              </tr>
            ) : (
              allocations.map((allocation) => (
                <tr key={allocation.id}>
                  <td>{allocation.id}</td>
                  <td>{allocation.student}</td>
                  <td>{allocation.hostel}</td>
                  <td>{allocation.room_number || "-"}</td>
                  <td>{new Date(allocation.allocated_on).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
