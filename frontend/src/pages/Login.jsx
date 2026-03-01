import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";

export default function Login({ onLogin, onToast }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.login({ username, password });
      const authenticated = await onLogin?.({ retries: 4, delayMs: 350 });
      if (!authenticated) {
        throw new Error("Login successful but session not established. Tafadhali jaribu tena.");
      }
      onToast?.("Login successful", "success");
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
      onToast?.(err.message, "error");
    }
  }

  return (
    <div className="auth-box">
      <h2>LOGIN</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit} className="form-grid">
        <label htmlFor="username">Username</label>
        <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit">Login</button>
      </form>
      <p>Don&apos;t have an account? <Link to="/register">Register</Link></p>
    </div>
  );
}
