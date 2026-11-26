from fastapi import FastAPI

from src.middleware.auth_middleware import DummyAuthMiddleware
from src.routers.message_router import router as message_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Clean Architecture FastAPI Basics",
        description="Simple layered FastAPI example with dummy auth middleware.",
        version="0.1.0",
    )

    # 1. Register Middleware (wraps incoming requests & outgoing responses)
    app.add_middleware(DummyAuthMiddleware)

    # 2. Register Routers (maps HTTP URLs to handlers)
    app.include_router(message_router)

    return app


app = create_app()
