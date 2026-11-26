# ⚛️ React Frontend — Developer Guide (with URL-Based Routing)

A step-by-step explanation of the React frontend that integrates with our
FastAPI backend for registration, login, and accessing protected endpoints
using **URL-based routing** with `react-router-dom`.

---

## Table of Contents

1. [What Was Built](#1-what-was-built)
2. [Project Structure](#2-project-structure)
3. [Libraries Used & Why](#3-libraries-used--why)
4. [URL Routes Overview](#4-url-routes-overview)
5. [How to Run](#5-how-to-run)
6. [File-by-File Walkthrough](#6-file-by-file-walkthrough)
   - [package.json](#61-packagejson--project-manifest)
   - [vite.config.js](#62-viteconfigjs--build--dev-server)
   - [index.html](#63-indexhtml--the-html-shell)
   - [main.jsx](#64-mainjsx--react-entry-point)
   - [App.jsx](#65-appjsx--routes--route-guarding)
   - [services/api.js](#66-servicesapijs--api-helper)
   - [RegisterForm.jsx](#67-registerformjsx)
   - [LoginForm.jsx](#68-loginformjsx)
   - [Dashboard.jsx](#69-dashboardjsx)
   - [App.css](#610-appcss--styles)
7. [React Router Concepts Explained](#7-react-router-concepts-explained)
8. [How the Auth Flow Works (Frontend)](#8-how-the-auth-flow-works-frontend)
9. [How the Vite Proxy Works](#9-how-the-vite-proxy-works)
10. [How Token Storage Works](#10-how-token-storage-works)
11. [Common Questions](#11-common-questions)

---

## 1. What Was Built

A Single-Page Application (SPA) with **URL-based routing**:

| URL Route | Component | Access | Description |
|---|---|---|---|
| `/login` | `LoginForm` | Public | Enter username & password to receive JWT |
| `/register` | `RegisterForm` | Public | Create new account and get JWT |
| `/dashboard` | `Dashboard` | Protected | View and add users (requires JWT) |
| `*` (any other URL) | — | — | Redirects automatically to `/login` |

If an unauthenticated user visits `/dashboard`, the app automatically redirects them to `/login`.
When a user logs in or registers successfully, they are programmatically navigated to `/dashboard`.

---

## 2. Project Structure

```
frontend/
├── index.html                  # Single HTML page shell
├── package.json                # Dependencies & scripts
├── vite.config.js              # Vite dev server + API proxy
│
└── src/
    ├── main.jsx                # Mounts React into the DOM
    ├── App.jsx                 # Routes & ProtectedRoute setup
    ├── App.css                 # All styles
    │
    ├── components/
    │   ├── RegisterForm.jsx    # /register component
    │   ├── LoginForm.jsx       # /login component
    │   └── Dashboard.jsx       # /dashboard component
    │
    └── services/
        └── api.js              # fetch() helper for FastAPI endpoints
```

---

## 3. Libraries Used & Why

### Production dependencies:

| Library | Version | What it is | Why we use it |
|---|---|---|---|
| **react** | ^19 | Core UI library | Builds reusable component-driven user interfaces |
| **react-dom** | ^19 | DOM renderer | Connects React components to browser HTML elements |
| **react-router-dom** | ^7 | Routing library for web | Enables client-side URL routing (`<BrowserRouter>`, `<Routes>`, `<Route>`, `<Link>`, `useNavigate`) |

### Dev dependencies:

| Library | Version | What it is | Why we use it |
|---|---|---|---|
| **vite** | ^6 | Build tool & dev server | Lightning-fast HMR (hot module replacement) & API proxying |
| **@vitejs/plugin-react** | ^4 | Vite React plugin | Compiles JSX and enables React fast refresh |

### What we intentionally did NOT use:
- **axios**: Browser-native `fetch()` is built-in and handles JSON requests/responses cleanly.
- **Redux / Zustand**: Auth state is stored in `localStorage` and URL paths represent navigation state.
- **UI frameworks**: Pure CSS provides full clarity on how styling functions.

---

## 4. URL Routes Overview

Client-side routing allows navigation between URLs without triggering full page reloads:

```
                  ┌──────────────────────┐
                  │      User Visits     │
                  └──────────┬───────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
       /login or /register                /dashboard
            │                                 │
     (Public access)                   Has JWT token?
            │                           │          │
    Renders Auth Form                  Yes         No
                                        │          │
                                   Renders     Redirects to
                                  Dashboard      /login
```

---

## 5. How to Run

Run in **two separate terminal windows**:

### Terminal 1 — Backend (FastAPI)
```bash
cd d:\Learning\Python\clean-architecture-3.0
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend (React)
```bash
cd d:\Learning\Python\clean-architecture-3.0\frontend
npm run dev
```

Open: **http://localhost:3000**
- Visiting `http://localhost:3000` redirects to `http://localhost:3000/login`
- Visiting `http://localhost:3000/register` opens registration
- Visiting `http://localhost:3000/dashboard` directly without logging in redirects to `/login`

---

## 6. File-by-File Walkthrough

### 6.1. `package.json` — Project Manifest

Lists project metadata and dependencies. Notice `react-router-dom` is included in `dependencies`:

```json
{
  "name": "clean-arch-frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "react-router-dom": "^7.9.6"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.5.2",
    "vite": "^6.3.5"
  }
}
```

---

### 6.2. `vite.config.js` — Build & Dev Server

Configures the local dev server on port `3000` and proxies any request starting with `/api` to FastAPI running on `localhost:8000`:

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

---

### 6.3. `index.html` — The HTML Shell

The single HTML file served to the client:
```html
<div id="root"></div>
<script type="module" src="/src/main.jsx"></script>
```

---

### 6.4. `main.jsx` — React Entry Point

Mounts the root `<App />` component into `#root`:
```jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./App.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

---

### 6.5. `App.jsx` — Routes & Route Guarding

This file defines the routing structure and route-protection logic:

```jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./components/LoginForm";
import RegisterForm from "./components/RegisterForm";
import Dashboard from "./components/Dashboard";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");
  if (!token) {
    // If no token exists, immediately redirect to /login
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />

        {/* Protected Route */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Catch-all Route: redirect everything else to /login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
```

**Key parts:**
1. `<BrowserRouter>`: Powers client-side routing using the browser's HTML5 History API (`pushState`, `replaceState`).
2. `<Routes>`: Evaluates child routes and renders the component matching current `window.location.pathname`.
3. `<Route>`: Maps a URL path (e.g. `/dashboard`) to a React element (`<Dashboard />`).
4. `<ProtectedRoute>`: A Higher-Order wrapper component. It inspects `localStorage` for a `token`. If absent, renders `<Navigate to="/login" replace />`.
5. `<Route path="*">`: Catch-all wildcard that guarantees invalid URLs route back to `/login`.

---

### 6.6. `services/api.js` — API Helper

Encapsulates all `fetch()` calls to keep HTTP details separate from components:

```js
const BASE_URL = "/api";

export async function post(endpoint, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const data = await response.json();
  return { ok: response.ok, status: response.status, data };
}

export async function get(endpoint, token) {
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${BASE_URL}${endpoint}`, { headers });
  const data = await response.json();
  return { ok: response.ok, status: response.status, data };
}

export async function del(endpoint, token) {
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "DELETE",
    headers,
  });
  const data = await response.json();
  return { ok: response.ok, status: response.status, data };
}
```

---

### 6.7. `RegisterForm.jsx`

Rendered at `/register`:
- Sends `POST /auth/register`
- On success: saves token to `localStorage` and calls `navigate("/dashboard")`
- Uses `<Link to="/login">` for instant client-side switching to the login page

```jsx
import { useNavigate, Link } from "react-router-dom";

export default function RegisterForm() {
  const navigate = useNavigate();
  // ... state ...

  async function handleSubmit(e) {
    e.preventDefault();
    const result = await post("/auth/register", { username, password });
    if (result.ok) {
      localStorage.setItem("token", result.data.access_token);
      navigate("/dashboard");
    } else {
      setError(result.data.detail || "Registration failed");
    }
  }

  return (
    // ...
    <Link to="/login" className="link-btn">Log in</Link>
  );
}
```

---

### 6.8. `LoginForm.jsx`

Rendered at `/login`:
- Sends `POST /auth/login`
- On success: saves token to `localStorage` and calls `navigate("/dashboard")`
- Uses `<Link to="/register">` to switch to registration

```jsx
import { useNavigate, Link } from "react-router-dom";

export default function LoginForm() {
  const navigate = useNavigate();
  // ... state ...

  async function handleSubmit(e) {
    e.preventDefault();
    const result = await post("/auth/login", { username, password });
    if (result.ok) {
      localStorage.setItem("token", result.data.access_token);
      navigate("/dashboard");
    } else {
      setError(result.data.detail || "Login failed");
    }
  }

  return (
    // ...
    <Link to="/register" className="link-btn">Register</Link>
  );
}
```

---

### 6.9. `Dashboard.jsx`

Rendered at `/dashboard`:
- Reads token from `localStorage.getItem("token")`
- Loads users using `get("/users/", token)` on initial load (`useEffect`)
- Allows adding new users using `post("/users/", { name, email }, token)`
- Prompts for confirmation and deletes users using `del("/users/{id}", token)`:
  ```js
  async function handleDeleteUser(user) {
    const confirmed = window.confirm(`Are you sure you want to delete "${user.name}"?`);
    if (!confirmed) return;
    await del(`/users/${user.id}`, token);
    fetchUsers();
  }
  ```
- Logout function removes token and redirects:
  ```js
  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }
  ```

---

### 6.10. `App.css` — Styles

Contains responsive styles for `.app`, `.auth-card`, `.dashboard`, `.link-btn`, and form inputs.

---

## 7. React Router Concepts Explained

### 1. `BrowserRouter`
Wraps the entire application. It subscribes to the browser's address bar and navigation events (`popstate`).

### 2. `Routes` and `Route`
`<Routes>` examines all child `<Route>` elements and selects the closest matching path. When URL changes, only the relevant component updates, avoiding full reloads.

### 3. `useNavigate()`
A React hook that returns an imperative navigation function:
```js
const navigate = useNavigate();
navigate("/dashboard"); // changes URL and displays Dashboard component
```

### 4. `<Link>`
Replaces regular HTML `<a>` tags. Standard `<a>` tags cause the browser to request a whole new page from the server. `<Link to="/path">` intercepts clicks, updates the browser URL bar, and tells React to swap components instantly in memory.

### 5. `<Navigate to="..." replace />`
Declarative redirection component. When rendered, it directs the user elsewhere. The `replace` prop replaces the current history entry so pressing the "Back" button doesn't trap the user in a redirect loop.

---

## 8. How the Auth Flow Works (Frontend)

```
1. User enters http://localhost:3000/
   └── Router evaluates "*" -> redirects to /login

2. User fills Login Form at /login -> clicks "Log In"
   ├── Sends POST /api/auth/login
   ├── Backend verifies password, returns JWT
   ├── Frontend saves token in localStorage: 'token' = 'eyJhbG...'
   └── Calls navigate("/dashboard") -> URL updates to /dashboard

3. /dashboard Route
   ├── ProtectedRoute checks localStorage.getItem("token")
   ├── Token exists -> renders <Dashboard />
   └── Dashboard fires useEffect -> GET /api/users/ with 'Authorization: Bearer <token>'

4. User clicks "Log out"
   ├── localStorage.removeItem("token")
   └── navigate("/login") -> URL returns to /login
```

---

## 9. How the Vite Proxy Works

```
Browser (localhost:3000)             Vite Dev Server              FastAPI (localhost:8000)
        │                                │                                │
        │  fetch("/api/auth/login")      │                                │
        │ ──────────────────────────────>│                                │
        │                                │  rewrite: /api → ""            │
        │                                │  forward: /auth/login          │
        │                                │ ──────────────────────────────>│
        │                                │                                │
        │                                │  <──── JSON response ────────│
        │  <──── JSON response ─────────│                                │
```

The frontend uses `/api/...` as its base URL. Vite strips `/api` and forwards the request directly to the FastAPI server on port 8000.

---

## 10. How Token Storage Works

```js
// Store token on login/register
localStorage.setItem("token", result.data.access_token);

// Access token in protected view / API calls
const token = localStorage.getItem("token");

// Remove token on logout
localStorage.removeItem("token");
```

---

## 11. Common Questions

### Why use `react-router-dom` instead of conditional state rendering?
URL-based routing gives users real browser URLs:
- Users can bookmark `/login` or `/dashboard`.
- The browser back/forward buttons work naturally.
- Direct links can be shared.
- Deep linking works seamlessly.

### How does `ProtectedRoute` prevent unauthorized access?
Before `<Dashboard />` is mounted, `<ProtectedRoute>` checks `localStorage.getItem("token")`. If the token is missing, it immediately renders `<Navigate to="/login" replace />`, blocking unauthorized rendering of dashboard UI components.

### What happens if the JWT token expires on the backend?
FastAPI returns `401 Unauthorized`. You can catch this in `api.js` or `Dashboard.jsx`, clear the token from `localStorage`, and navigate to `/login`.
