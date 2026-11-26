"""In-memory data resource simulating an external database connection.

In a layered architecture, the Resource layer owns raw connections and
infrastructure lifecycles (e.g., DB engine, connection pool, Redis client).
Tomorrow, when you attach a real database, you will add a `DatabaseResource`
here without modifying the Controller or Router layers.
"""

from datetime import datetime, timezone
from typing import Any


class MemoryResource:
    """Thread-safe-enough single-process in-memory store with lifecycle hooks."""

    def __init__(self) -> None:
        self._records: dict[int, dict[str, Any]] = {}
        self._next_id: int = 1
        self._connected: bool = False

    def connect(self) -> None:
        """Initialize the resource and load sample seed data."""
        if self._connected:
            return
        self._connected = True
        self._seed_initial_data()

    def disconnect(self) -> None:
        """Tear down the resource on application shutdown."""
        self._records.clear()
        self._next_id = 1
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Return whether the resource has been initialized."""
        return self._connected

    @property
    def records(self) -> dict[int, dict[str, Any]]:
        """Expose raw storage dictionary to the Repository layer."""
        return self._records

    def next_id(self) -> int:
        """Generate the next sequential integer ID."""
        current = self._next_id
        self._next_id += 1
        return current

    def _seed_initial_data(self) -> None:
        """Populate a couple of sample items so GET /items returns data immediately."""
        now = datetime.now(timezone.utc)
        sample_items = [
            {
                "name": "Clean Architecture Guide",
                "description": "Learn how Middleware, Router, Controller, Repository, and Resource work together.",
                "created_by": "system",
                "created_at": now,
            },
            {
                "name": "FastAPI Starter",
                "description": "Minimal layered backend ready for future database integration.",
                "created_by": "system",
                "created_at": now,
            },
        ]
        for item in sample_items:
            item_id = self.next_id()
            self._records[item_id] = {"id": item_id, **item}
