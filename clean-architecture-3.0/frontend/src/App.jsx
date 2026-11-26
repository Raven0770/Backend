/**
 * App.jsx — Root Component with URL-Based Routing
 *
 * Uses react-router-dom to map URLs to components:
 *   /login     → LoginForm
 *   /register  → RegisterForm
 *   /dashboard → Dashboard (protected — redirects to /login if no token)
 *
 * BrowserRouter: Uses the browser's History API to keep the URL in sync
 *   with what's shown on screen, without full page reloads.
 *
 * Routes: Renders the first <Route> whose path matches the current URL.
 *
 * Navigate: A component that immediately redirects to another URL
 *   when rendered (used for protecting routes and default redirects).
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./components/LoginForm";
import RegisterForm from "./components/RegisterForm";
import Dashboard from "./components/Dashboard";

/**
 * ProtectedRoute — a wrapper that checks for a JWT token.
 *
 * If a token exists in localStorage → render the child component.
 * If not → redirect to /login.
 *
 * Usage:
 *   <Route path="/dashboard" element={
 *     <ProtectedRoute><Dashboard /></ProtectedRoute>
 *   } />
 */
function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");
  if (!token) {
    // No token → redirect to login
    // "replace" prevents the protected URL from appearing in browser history
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />

        {/* Protected route — only accessible with a token */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Default: redirect unknown paths to /login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
