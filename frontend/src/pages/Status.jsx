import { useEffect, useState } from "react";
import { api } from "../api";
import { useLanguage } from "../language";

export default function Status() {
  const { t } = useLanguage();
  const [allocation, setAllocation] = useState(null);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  async function loadStatus() {
    const res = await api.status();
    setAllocation(res.allocation);
    setError("");
  }

  useEffect(() => {
    loadStatus().catch((err) => setError(err.message));

    const intervalId = window.setInterval(() => {
      loadStatus().catch(() => {});
    }, 15000);

    return () => window.clearInterval(intervalId);
  }, []);

  async function handleRefreshNow() {
    setRefreshing(true);
    try {
      await loadStatus();
    } catch (err) {
      setError(err.message);
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <section className="section">
      <h2>{t("allocationStatus")}</h2>
      <div className="actions-row">
        <button type="button" onClick={handleRefreshNow} disabled={refreshing}>
          {refreshing ? "Refreshing..." : "Refresh now"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      {!error && !allocation && <p>{t("pendingStatus")}</p>}
      {allocation && (
        <div>
          <p>{t("allocatedTo")} <strong>{allocation.hostel_name}</strong></p>
          <p>{t("room")}: <strong>{allocation.room_number || t("notAssigned")}</strong></p>
          <p>{t("allocatedOn")}: {new Date(allocation.allocated_on).toLocaleString()}</p>
        </div>
      )}
    </section>
  );
}
