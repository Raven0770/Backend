"""Dummy authentication middleware for learning FastAPI middleware flow.

Every incoming HTTP request enters this middleware BEFORE reaching any router.
- Public paths (health check, OpenAPI docs) bypass authentication.
- Protected paths must include `Authorization: Bearer <token>`.
- On success, a `UserContext` object is stored on `request.state.user` so
  downstream dependencies and controllers can identify the caller.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings
from app.schemas.item_schema import UserContext


class AuthMiddleware(BaseHTTPMiddleware):
    """Validates a dummy Bearer token on non-public HTTP routes."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Allow CORS preflight and public documentation/health routes without a token.
        if request.method == "OPTIONS" or request.url.path in settings.public_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Missing or invalid Authorization header. Expected 'Bearer <token>'."
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.removeprefix("Bearer ").strip()
        valid_tokens = settings.get_tokens()
        username = valid_tokens.get(token)

        if username is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired authentication token."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Attach authenticated user info to request.state for downstream layers.
        request.state.user = UserContext(username=username, token=token)

        # Forward the request to the Router -> Controller -> Repository -> Resource chain.
        response = await call_next(request)
        response.headers["X-Authenticated-User"] = username
        return response
