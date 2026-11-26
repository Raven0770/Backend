/**
 * api.js — API Service
 *
 * A thin wrapper around the browser's built-in fetch() function.
 * Centralises the base URL and headers so every component doesn't
 * have to repeat them.
 *
 * No external HTTP library (like axios) is needed — fetch() is
 * built into every modern browser.
 */

// In development, Vite proxies "/api" → "http://localhost:8000"
// (configured in vite.config.js). So "/api/auth/login" becomes
// "http://localhost:8000/auth/login" behind the scenes.
const BASE_URL = "/api";

/**
 * Send a POST request with a JSON body.
 *
 * @param {string} endpoint - e.g. "/auth/login"
 * @param {object} body     - the data to send
 * @param {string} [token]  - optional JWT token for protected routes
 * @returns {object}        - { ok, status, data }
 */
export async function post(endpoint, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return { ok: response.ok, status: response.status, data };
}

/**
 * Send a GET request with the JWT token attached.
 *
 * @param {string} endpoint - e.g. "/users/"
 * @param {string} token    - the JWT access token
 * @returns {object}        - { ok, status, data }
 */
export async function get(endpoint, token) {
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, { headers });
  const data = await response.json();
  return { ok: response.ok, status: response.status, data };
}

/**
 * Send a DELETE request with the JWT token attached.
 *
 * @param {string} endpoint - e.g. "/users/1"
 * @param {string} [token]  - the JWT access token
 * @returns {object}        - { ok, status, data }
 */
export async function del(endpoint, token) {
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "DELETE",
    headers,
  });
  const data = await response.json();
  return { ok: response.ok, status: response.status, data };
}

