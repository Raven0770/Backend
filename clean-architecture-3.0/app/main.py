"""
Application Entry Point — main.py

This file creates the FastAPI application instance, registers
middleware (CORS + JWT Auth), and includes routers.

Run the app with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.auth import JWTAuthMiddleware
from app.routers import auth_router, user_router

# --- Create the FastAPI app ---
app = FastAPI(
    title="Clean Architecture Demo",
    description="A simple FastAPI project to understand layered architecture with JWT auth",
    version="2.0.0",
)

"""
# ---------- CORS Middleware ---------- #
#
# CORS = Cross-Origin Resource Sharing.
# Browsers block requests from one domain (origin) to another by default.
# For example, a React app on http://localhost:3000 calling your API on
# http://localhost:8000 would be blocked without CORS headers.
#
# This middleware adds the necessary HTTP headers so the browser allows it.
#
# Configuration:
#   allow_origins  → which domains can call your API
#   allow_methods  → which HTTP methods are allowed (GET, POST, etc.)
#   allow_headers  → which custom headers the client can send
#
# For development, we allow everything ("*"). In production, replace
# "*" with your actual frontend domain(s).
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # In production: ["https://yourfrontend.com"]
    allow_credentials=True,
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"],           # Allow all headers (including Authorization)
)

# ---------- JWT Auth Middleware ---------- #
# Runs on every request AFTER CORS (middleware order is bottom-to-top
# in FastAPI — the last one added runs first).
app.add_middleware(JWTAuthMiddleware)

# --- Register routers ---
app.include_router(auth_router.router)
app.include_router(user_router.router)


# --- Root endpoint (public — no auth needed) ---
@app.get("/", tags=["Health"])
def root():
    """Welcome page — confirms the server is running."""
    return {"message": "Welcome to Clean Architecture Demo API", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health_check():
    """Simple endpoint to check if the server is alive."""
    return {"status": "ok"}
