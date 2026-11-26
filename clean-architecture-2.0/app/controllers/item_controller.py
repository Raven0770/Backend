"""Item controller containing business rules independent of HTTP transport.

Notice that this layer:
1. Depends ONLY on the `ItemRepository` interface (not `MemoryResource`).
2. Contains business logic (trimming names, preventing duplicates, checking existence).
3. Raises domain exceptions (`ItemNotFoundError`, `DuplicateItemError`) rather than
   coupling business rules to FastAPI's HTTP layer.
"""

from app.repositories.item_repository import ItemRepository
from app.schemas.item_schema import ItemCreate, ItemResponse, UserContext


class ItemNotFoundError(Exception):
    """Raised when a requested item does not exist."""

    def __init__(self, item_id: int) -> None:
        super().__init__(f"Item with id={item_id} was not found.")
        self.item_id = item_id


class DuplicateItemError(Exception):
    """Raised when attempting to create an item with an existing name."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Item with name '{name}' already exists.")
        self.name = name


class ItemController:
    """Coordinates item use cases between the Router and Repository layers."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    def list_items(self) -> list[ItemResponse]:
        """Return all available items."""
        return self._repository.list_all()

    def get_item(self, item_id: int) -> ItemResponse:
        """Fetch a single item or raise `ItemNotFoundError`."""
        item = self._repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item

    def create_item(self, payload: ItemCreate, user: UserContext) -> ItemResponse:
        """Validate business rules and delegate creation to the repository."""
        clean_name = payload.name.strip()
        if self._repository.get_by_name(clean_name) is not None:
            raise DuplicateItemError(clean_name)

        clean_description = payload.description.strip() if payload.description else None
        return self._repository.create(
            name=clean_name,
            description=clean_description,
            created_by=user.username,
        )

    def delete_item(self, item_id: int) -> None:
        """Delete an item or raise `ItemNotFoundError` if it does not exist."""
        deleted = self._repository.delete(item_id)
        if not deleted:
            raise ItemNotFoundError(item_id)
