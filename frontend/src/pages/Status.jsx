import { useEffect, useState } from "react";
import { api } from "../api";

export default function Status() {
  const [allocation, setAllocation] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.status()
      .then((res) => setAllocation(res.allocation))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section className="section">
      <h2>Your Allocation Status</h2>
      {error && <p className="error">{error}</p>}
      {!error && !allocation && <p>Your application is pending or you have not applied yet.</p>}
      {allocation && (
        <div>
          <p>You have been allocated to <strong>{allocation.hostel_name}</strong></p>
          <p>Room: <strong>{allocation.room_number || "Not assigned yet"}</strong></p>
          <p>Allocated on: {new Date(allocation.allocated_on).toLocaleString()}</p>
        </div>
      )}
    </section>
  );
}