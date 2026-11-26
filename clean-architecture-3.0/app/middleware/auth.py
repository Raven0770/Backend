"""
Middleware Layer — JWT Authentication

Middleware runs on EVERY request BEFORE it reaches any router.
It can inspect, modify, or reject requests globally.

This middleware:
  1. Checks if the request path is public (skip auth) or protected.
  2. For protected paths: reads the Authorization header, decodes the
     JWT token, and either allows or rejects the request.

CORS (Cross-Origin Resource Sharing) is configured separately in
main.py using FastAPI's built-in CORSMiddleware — that is the
standard place for it because CORS is an app-level concern, not
an auth concern.

Libraries used:
  - starlette.middleware.base.BaseHTTPMiddleware
    FastAPI is built on top of Starlette. BaseHTTPMiddleware lets
    you write middleware as a simple async function.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.utils.security import decode_access_token

# ---------- Public Paths Configuration ---------- #

# Paths that do NOT require a JWT token.
# Auth endpoints must be public (you can't login if login requires login!).
PUBLIC_PATHS: set[str] = {
    "/",              # root welcome
    "/health",        # health-check
    "/docs",          # Swagger UI
    "/redoc",         # ReDoc UI
    "/openapi.json",  # OpenAPI schema (Swagger needs this)
    "/auth/register", # registration endpoint
    "/auth/login",    # login endpoint
}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Reject requests to protected routes that lack a valid JWT.

    Flow:
      1. Is the path public? → let it through.
      2. Is there an Authorization header with "Bearer <token>"?
         → No? → 401 Unauthorized.
      3. Decode the JWT token.
         → Invalid or expired? → 401 Unauthorized.
      4. Token is valid → attach the username to request.state
         so downstream code (controllers, services) can access
         the current user without decoding the token again.
      5. Call call_next(request) to pass the request onward.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:

        # 1. Let public paths through without checking auth
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # 2. Read the Authorization header
        auth_header: str | None = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Missing or malformed Authorization header. "
                    "Expected: 'Bearer <your-jwt-token>'"
                },
            )

        # 3. Extract and decode the JWT token
        token = auth_header.removeprefix("Bearer ").strip()
        payload = decode_access_token(token)

        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token. Please log in again."},
            )

        # 4. Attach the current user to request.state
        # Any downstream code can access: request.state.current_user
        request.state.current_user = payload.get("sub")

        # 5. Token is valid — let the request continue
        response = await call_next(request)
        return response
