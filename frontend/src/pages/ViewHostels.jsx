import { useEffect, useState } from "react";
import { api } from "../api";

export default function ViewHostels() {
  const [hostels, setHostels] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.hostels()
      .then((res) => setHostels(res.hostels || []))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section className="section">
      <h2>Available Hostels</h2>
      {error && <p className="error">{error}</p>}
      <div className="cards">
        {hostels.length === 0 && !error && <p>No hostels found.</p>}
        {hostels.map((hostel) => (
          <div className="card" key={hostel.id}>
            <h3>{hostel.name}</h3>
            <p>Location: {hostel.location}</p>
            <p>Available Rooms: {hostel.total_rooms}</p>
          </div>
        ))}
      </div>
    </section>
  );
}