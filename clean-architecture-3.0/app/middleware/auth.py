"""
Middleware Layer — Dummy Authentication

Middleware runs on EVERY request, BEFORE it reaches any router.
It can inspect, modify, or reject requests globally.

This dummy auth middleware checks for a hardcoded API token in the
Authorization header. In a real app, you'd verify JWTs, session
cookies, or call an auth service here.

How it works:
  1. The request arrives.
  2. Middleware reads the Authorization header.
  3. If the path is in the public list (e.g. /docs), skip auth.
  4. Otherwise, reject with 401 if the token is missing/wrong.
  5. If valid, call `await call_next(request)` to pass the request
     down to the router → controller → service → repository chain.
  6. The response travels back up through the middleware.

Library used:
  - starlette.middleware.base.BaseHTTPMiddleware
    FastAPI is built on top of Starlette. BaseHTTPMiddleware is
    Starlette's helper class that lets you write middleware as a
    simple async function instead of raw ASGI plumbing.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

# ---------- Configuration ---------- #

# Hardcoded token for learning purposes.
# In production, store secrets in environment variables or a vault.
DUMMY_TOKEN = "my-secret-token-123"

# Paths that do NOT require authentication (public routes).
PUBLIC_PATHS: set[str] = {
    "/",           # root welcome
    "/health",     # health-check
    "/docs",       # Swagger UI
    "/redoc",      # ReDoc UI
    "/openapi.json",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """Reject requests that lack a valid Authorization header."""

    async def dispatch( 
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:

        # 1. Let public paths through without checking auth
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # 2. Read the Authorization header
        auth_header: str | None = request.headers.get("Authorization")

        # 3. Expect format: "Bearer <token>"
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or malformed Authorization header. "
                         "Expected: 'Bearer my-secret-token-123'"},
            )

        token = auth_header.removeprefix("Bearer ").strip()

        if token != DUMMY_TOKEN:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
            )

        # 4. Token is valid — let the request continue
        response = await call_next(request)
        return response
