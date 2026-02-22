import { useEffect, useState } from "react";
import { api } from "../api";

export default function Apply({ onToast }) {
  const [hostels, setHostels] = useState([]);
  const [hostelId, setHostelId] = useState("");
  const [message, setMessage] = useState("");
  const [assignedRoom, setAssignedRoom] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.hostels()
      .then((res) => setHostels(res.hostels || []))
      .catch((err) => setError(err.message));
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    setMessage("");
    setAssignedRoom("");
    setError("");
    try {
      const res = await api.apply({ hostel_id: hostelId });
      setMessage(res.message || "Application submitted");
      setAssignedRoom(res.room_number || "");
      onToast?.("Application submitted successfully", "success");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="section">
      <h2>Apply for Hostel</h2>
      <p className="subtitle">Select a hostel below and submit your application.</p>
      {message && <p className="success">{message}</p>}
      {assignedRoom && <p className="success">Room Number: <strong>{assignedRoom}</strong></p>}
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit} className="form-grid">
        <label htmlFor="hostel">Preferred Hostel</label>
        <select id="hostel" value={hostelId} onChange={(e) => setHostelId(e.target.value)} required>
          <option value="">-- Select hostel --</option>
          {hostels.map((hostel) => (
            <option key={hostel.id} value={hostel.id}>
              {hostel.name} - {hostel.location}
            </option>
          ))}
        </select>
        <button type="submit">Submit Application</button>
      </form>
    </section>
  );
}
