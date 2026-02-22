import { useEffect, useState } from "react";
import { api } from "../api";
import { useLanguage } from "../language";

export default function Status() {
  const { t } = useLanguage();
  const [allocation, setAllocation] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.status()
      .then((res) => setAllocation(res.allocation))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section className="section">
      <h2>{t("allocationStatus")}</h2>
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
