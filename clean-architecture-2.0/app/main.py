"""FastAPI application entry point and composition root."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.controllers.item_controller import DuplicateItemError, ItemNotFoundError
from app.middleware.auth import AuthMiddleware
from app.resources.memory_resource import MemoryResource
from app.routers import health_router, item_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup and shutdown of backing resources (e.g., memory store or DB)."""
    resource = MemoryResource()
    resource.connect()
    app.state.memory_resource = resource
    try:
        yield
    finally:
        resource.disconnect()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    # 1. Middleware layer (runs on every HTTP request before routers)
    app.add_middleware(AuthMiddleware)

    # 2. Domain-to-HTTP exception mapping (keeps Controllers HTTP-agnostic)
    @app.exception_handler(ItemNotFoundError)
    async def item_not_found_handler(
        request: Request,
        exc: ItemNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DuplicateItemError)
    async def duplicate_item_handler(
        request: Request,
        exc: DuplicateItemError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    # 3. Router layer
    app.include_router(health_router.router)
    app.include_router(item_router.router, prefix=settings.api_prefix)

    return app


app = create_app()
