"""Central Dependency Injection (DI) container using FastAPI `Depends`.

This file is the ONLY place that wires concrete implementations to interfaces.
Tomorrow, when you attach a database:
1. Create `DatabaseResource` in `app/resources/` and initialize it in `main.py` lifespan.
2. Create `SqlItemRepository` in `app/repositories/`.
3. Update `get_item_repository` below to return `SqlItemRepository(...)`.
Controllers and Routers do not need to change at all.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.controllers.item_controller import ItemController
from app.repositories.item_repository import InMemoryItemRepository, ItemRepository
from app.resources.memory_resource import MemoryResource
from app.schemas.item_schema import UserContext


def get_memory_resource(request: Request) -> MemoryResource:
    """Retrieve the shared MemoryResource initialized during app lifespan."""
    return request.app.state.memory_resource


def get_item_repository(
    resource: Annotated[MemoryResource, Depends(get_memory_resource)],
) -> ItemRepository:
    """Provide the repository implementation behind the `ItemRepository` interface."""
    return InMemoryItemRepository(resource=resource)


def get_item_controller(
    repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemController:
    """Construct the controller with its required repository dependency."""
    return ItemController(repository=repository)


def get_current_user(request: Request) -> UserContext:
    """Read the authenticated `UserContext` attached by `AuthMiddleware`."""
    user: UserContext | None = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication context is missing.",
        )
    return user
