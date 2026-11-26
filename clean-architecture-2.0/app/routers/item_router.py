"""Router layer for item endpoints.

Responsibilities of the Router layer:
- Define HTTP paths, methods, status codes, and response schemas.
- Extract validated request payloads and inject dependencies via `Depends`.
- Delegate work to the Controller layer and return the result.
- NEVER contain business logic or direct storage access.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPBearer

from app.controllers.item_controller import ItemController
from app.dependencies import get_current_user, get_item_controller
from app.schemas.item_schema import ItemCreate, ItemResponse, UserContext

# Registers Bearer auth in OpenAPI (/docs) "Authorize" modal;
# actual token verification is enforced globally by AuthMiddleware.
bearer_scheme = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/items",
    tags=["Items"],
    dependencies=[Depends(bearer_scheme)],
)


@router.get("", response_model=list[ItemResponse])
def list_items(
    controller: Annotated[ItemController, Depends(get_item_controller)],
) -> list[ItemResponse]:
    """Retrieve all items."""
    return controller.list_items()


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    controller: Annotated[ItemController, Depends(get_item_controller)],
) -> ItemResponse:
    """Retrieve a single item by its integer ID."""
    return controller.get_item(item_id)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    controller: Annotated[ItemController, Depends(get_item_controller)],
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> ItemResponse:
    """Create a new item attributed to the authenticated middleware user."""
    return controller.create_item(payload=payload, user=current_user)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    controller: Annotated[ItemController, Depends(get_item_controller)],
) -> Response:
    """Delete an item by ID."""
    controller.delete_item(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
