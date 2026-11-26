"""Public health and root routes (excluded from auth middleware)."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import get_memory_resource
from app.resources.memory_resource import MemoryResource
from app.schemas.item_schema import MessageResponse

router = APIRouter(tags=["Health"])


@router.get("/", response_model=MessageResponse)
def root() -> MessageResponse:
    """Basic welcome endpoint."""
    return MessageResponse(
        status="ok",
        message=f"{settings.app_name} is running. Visit /docs to explore the API.",
    )


@router.get("/health", response_model=MessageResponse)
def health_check(
    resource: Annotated[MemoryResource, Depends(get_memory_resource)],
) -> MessageResponse:
    """Verify the application and its backing resource are ready."""
    state = "connected" if resource.is_connected else "disconnected"
    return MessageResponse(
        status="healthy",
        message=f"Backing resource state: {state}",
    )
