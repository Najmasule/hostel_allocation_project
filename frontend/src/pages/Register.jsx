import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";

export default function Register({ onRegister, onToast }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    username: "",
    password: "",
    password2: "",
    adress: "",
    phone_number: ""
  });
  const [error, setError] = useState("");

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.register(form);
      const authenticated = await onRegister?.();
      if (!authenticated) {
        throw new Error("Register successful but session not established. Tafadhali login.");
      }
      onToast?.("Register successful", "success");
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
      onToast?.(err.message, "error");
    }
  }

  return (
    <div className="auth-box">
      <h2>REGISTER</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit} className="form-grid">
        <label htmlFor="name">Full Name</label>
        <input id="name" value={form.name} onChange={(e) => update("name", e.target.value)} required />
        <label htmlFor="username">Username</label>
        <input id="username" value={form.username} onChange={(e) => update("username", e.target.value)} required />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" value={form.password} onChange={(e) => update("password", e.target.value)} required />
        <label htmlFor="password2">Confirm Password</label>
        <input id="password2" type="password" value={form.password2} onChange={(e) => update("password2", e.target.value)} required />
        <label htmlFor="adress">Address (optional)</label>
        <input id="adress" value={form.adress} onChange={(e) => update("adress", e.target.value)} />
        <label htmlFor="phone">Phone Number (optional)</label>
        <input id="phone" value={form.phone_number} onChange={(e) => update("phone_number", e.target.value)} />
        <button type="submit">Register</button>
      </form>
      <p>Already registered? <Link to="/">Login</Link></p>
    </div>
  );
}
