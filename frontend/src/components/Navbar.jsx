import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="nav">
      <NavLink to="/dashboard">Home</NavLink>
      <NavLink to="/hostels">View Hostel</NavLink>
      <NavLink to="/apply">Apply for Hostel</NavLink>
      <NavLink to="/status">Allocation Status</NavLink>
      <NavLink to="/settings">Settings</NavLink>
    </nav>
  );
}