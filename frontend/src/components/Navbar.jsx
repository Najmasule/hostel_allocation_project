import { NavLink } from "react-router-dom";
import { useLanguage } from "../language";

export default function Navbar({ currentUser }) {
  const { t } = useLanguage();
  const isAdmin = Boolean(currentUser?.is_admin);

  return (
    <nav className="nav">
      <NavLink to="/dashboard">{t("home")}</NavLink>
      {isAdmin && <NavLink to="/admin-dashboard">Admin Dashboard</NavLink>}
      {isAdmin && <NavLink to="/admin-activity">Admin Activity</NavLink>}
      <NavLink to="/hostels">{t("viewHostel")}</NavLink>
      <NavLink to="/apply">{t("applyHostel")}</NavLink>
      <NavLink to="/status">{t("status")}</NavLink>
      <NavLink to="/settings">{t("settings")}</NavLink>
    </nav>
  );
}
