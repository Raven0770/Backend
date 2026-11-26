/**
 * main.jsx — React Entry Point
 *
 * This file mounts the React app into the DOM.
 * It finds the <div id="root"> in index.html and renders
 * the <App /> component inside it.
 *
 * StrictMode: A development helper that warns about unsafe
 * patterns. It doesn't affect production builds.
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./App.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
