/**
 * Dashboard.jsx — Post-Login View
 *
 * Shown after successful login/register at /dashboard.
 * Demonstrates:
 *   1. Reading the JWT token from localStorage.
 *   2. Calling protected API endpoints with the token.
 *   3. Logging out (clear token + navigate to /login).
 *
 * Uses react-router-dom:
 *   useNavigate() — redirect to /login on logout
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { get, post, del } from "../services/api";

export default function Dashboard() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const [users, setUsers] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  // Fetch users on first render
  useEffect(() => {
    fetchUsers();
  }, []);

  async function fetchUsers() {
    const result = await get("/users/", token);
    if (result.ok) {
      setUsers(result.data);
    }
  }

  async function handleAddUser(e) {
    e.preventDefault();
    setMessage("");

    const result = await post("/users/", { name, email }, token);

    if (result.ok) {
      setMessage(`User "${result.data.name}" created!`);
      setName("");
      setEmail("");
      fetchUsers(); // refresh the list
    } else {
      setMessage(result.data.detail || "Failed to create user");
    }
  }

  async function handleDeleteUser(user) {
    const confirmed = window.confirm(`Are you sure you want to delete "${user.name}"?`);
    if (!confirmed) return;

    setMessage("");
    const result = await del(`/users/${user.id}`, token);

    if (result.ok) {
      setMessage(`User "${user.name}" deleted successfully!`);
      fetchUsers(); // refresh the list
    } else {
      setMessage(result.data.detail || "Failed to delete user");
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <div className="dashboard">
      <header>
        <h2>Dashboard</h2>
        <button onClick={handleLogout} className="logout-btn">
          Log out
        </button>
      </header>

      <section className="add-user">
        <h3>Add a User</h3>
        <form onSubmit={handleAddUser}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            required
          />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
          />
          <button type="submit">Add</button>
        </form>
        {message && <p className="info">{message}</p>}
      </section>

      <section className="user-list">
        <h3>Users ({users.length})</h3>
        {users.length === 0 ? (
          <p className="empty">No users yet. Add one above!</p>
        ) : (
          <ul>
            {users.map((u) => (
              <li key={u.id} className="user-item">
                <span className="user-info">
                  <strong>{u.name}</strong> — {u.email}
                </span>
                <button
                  type="button"
                  onClick={() => handleDeleteUser(u)}
                  className="delete-btn"
                  title={`Delete ${u.name}`}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
