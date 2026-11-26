"""Item repository interface and in-memory implementation.

The Repository layer sits between the Controller and the Resource layer:
- It defines an abstract contract (`ItemRepository`) describing *what* data
  operations exist, without revealing *how* or *where* data is stored.
- `InMemoryItemRepository` fulfills that contract using `MemoryResource`.
- Tomorrow, you can write `SqlItemRepository` implementing `ItemRepository`
  and swap it in `app/dependencies.py`—zero changes needed in Controllers!
"""

from datetime import datetime, timezone
from typing import Protocol

from app.resources.memory_resource import MemoryResource
from app.schemas.item_schema import ItemResponse


class ItemRepository(Protocol):
    """Contract that any item storage backend must satisfy."""

    def list_all(self) -> list[ItemResponse]:
        """Return all stored items."""
        ...

    def get_by_id(self, item_id: int) -> ItemResponse | None:
        """Return a single item by ID, or None if it does not exist."""
        ...

    def get_by_name(self, name: str) -> ItemResponse | None:
        """Return a single item matching name (case-insensitive), or None."""
        ...

    def create(self, name: str, description: str | None, created_by: str) -> ItemResponse:
        """Persist a new item and return its stored representation."""
        ...

    def delete(self, item_id: int) -> bool:
        """Delete an item by ID. Return True if deleted, False if not found."""
        ...


class InMemoryItemRepository:
    """In-memory implementation of `ItemRepository` backed by `MemoryResource`."""

    def __init__(self, resource: MemoryResource) -> None:
        self._resource = resource

    def list_all(self) -> list[ItemResponse]:
        """Map all raw records from MemoryResource into ItemResponse schemas."""
        return [
            ItemResponse(**record)
            for record in self._resource.records.values()
        ]

    def get_by_id(self, item_id: int) -> ItemResponse | None:
        """Look up one raw record by primary key."""
        record = self._resource.records.get(item_id)
        if record is None:
            return None
        return ItemResponse(**record)

    def get_by_name(self, name: str) -> ItemResponse | None:
        """Find an existing item with the same normalized name."""
        target = name.strip().lower()
        for record in self._resource.records.values():
            if record["name"].strip().lower() == target:
                return ItemResponse(**record)
        return None

    def create(self, name: str, description: str | None, created_by: str) -> ItemResponse:
        """Allocate a new ID in MemoryResource and store the record."""
        item_id = self._resource.next_id()
        record = {
            "id": item_id,
            "name": name,
            "description": description,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc),
        }
        self._resource.records[item_id] = record
        return ItemResponse(**record)

    def delete(self, item_id: int) -> bool:
        """Remove a record from MemoryResource if present."""
        return self._resource.records.pop(item_id, None) is not None
