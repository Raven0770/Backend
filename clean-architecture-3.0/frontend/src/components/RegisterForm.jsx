/**
 * RegisterForm.jsx — Registration Component
 *
 * A simple form with username + password fields.
 * On submit, it calls POST /auth/register and receives a JWT token.
 *
 * Uses react-router-dom:
 *   useNavigate() — programmatically navigate to another URL
 *   Link          — renders an <a> tag that navigates without page reload
 */

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { post } from "../services/api";

export default function RegisterForm() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    // Prevent the browser's default form submission (which reloads the page)
    e.preventDefault();
    setError("");
    setLoading(true);

    const result = await post("/auth/register", { username, password });

    if (result.ok) {
      // Registration successful — store token and navigate to dashboard
      localStorage.setItem("token", result.data.access_token);
      navigate("/dashboard");
    } else {
      // Show the error message from the backend
      setError(result.data.detail || "Registration failed");
    }

    setLoading(false);
  }

  return (
    <div className="app">
      <h1>🏗️ Clean Architecture Demo</h1>
      <div className="auth-card">
        <h2>Create Account</h2>

        <form onSubmit={handleSubmit}>
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. alice"
              required
              minLength={3}
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="min. 6 characters"
              required
              minLength={6}
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Creating…" : "Register"}
          </button>
        </form>

        <p className="switch">
          Already have an account?{" "}
          <Link to="/login" className="link-btn">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
