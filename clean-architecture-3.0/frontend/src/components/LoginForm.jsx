/**
 * LoginForm.jsx — Login Component
 *
 * A simple form with username + password fields.
 * On submit, it calls POST /auth/login and receives a JWT token.
 *
 * Uses react-router-dom:
 *   useNavigate() — programmatically navigate to /dashboard after login
 *   Link          — navigate to /register without page reload
 */

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { post } from "../services/api";

export default function LoginForm() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const result = await post("/auth/login", { username, password });

    if (result.ok) {
      // Store token and navigate to dashboard
      localStorage.setItem("token", result.data.access_token);
      navigate("/dashboard");
    } else {
      setError(result.data.detail || "Login failed");
    }

    setLoading(false);
  }

  return (
    <div className="app">
      <h1>🏗️ Clean Architecture Demo</h1>
      <div className="auth-card">
        <h2>Log In</h2>

        <form onSubmit={handleSubmit}>
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. alice"
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="your password"
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Logging in…" : "Log In"}
          </button>
        </form>

        <p className="switch">
          Don't have an account?{" "}
          <Link to="/register" className="link-btn">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
