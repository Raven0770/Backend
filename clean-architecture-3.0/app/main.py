"""
Application Entry Point — main.py

This file creates the FastAPI application instance, registers
middleware, and includes routers. It's the "glue" that ties
every layer together.

Run the app with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.middleware.auth import AuthMiddleware
from app.routers import user_router

# --- Create the FastAPI app ---
app = FastAPI(
    title="Clean Architecture Demo",
    description="A simple FastAPI project to understand layered architecture",
    version="1.0.0",
)

# --- Register middleware (runs on EVERY request) ---
app.add_middleware(AuthMiddleware)

# --- Register routers ---
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
