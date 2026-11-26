from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Public endpoints that do not require authentication
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

# Hardcoded dummy token & user (replaces DB/JWT lookup for learning)
DUMMY_VALID_TOKEN = "dummy-token"
DUMMY_USER = "dummy-user"


class DummyAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware Layer:
    Runs BEFORE every route handler and AFTER the route returns a response.
    Validates a dummy Bearer token without touching any database.
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        expected_header = f"Bearer {DUMMY_VALID_TOKEN}"

        if auth_header != expected_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": (
                        "Unauthorized: Send header "
                        f"'Authorization: {expected_header}' to access this route."
                    ),
                },
            )

        # Attach dummy user info so downstream Router/Controller can read it
        request.state.user = DUMMY_USER

        response = await call_next(request)
        response.headers["X-Auth-Status"] = "authenticated"
        return response
