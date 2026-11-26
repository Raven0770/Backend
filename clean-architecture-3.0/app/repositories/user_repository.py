"""
Repository Layer — User Repository

The repository is the ONLY place that talks to your data source.
Right now it uses a simple Python dict (in-memory storage).

Tomorrow, you can swap this dict with a real database (SQLAlchemy,
MongoDB, etc.) and NOTHING else in the app needs to change — that's
the whole point of this layer.
"""

from app.models.user import UserCreate


class UserRepository:
    """Handles all data access for users."""

    def __init__(self) -> None:
        # In-memory "database" — a dict keyed by user id
        self._storage: dict[int, dict] = {}
        self._next_id: int = 1

    # ---------- CRUD operations ---------- #

    def get_all(self) -> list[dict]:
        """Return every user."""
        return list(self._storage.values())

    def get_by_id(self, user_id: int) -> dict | None:
        """Return one user or None if not found."""
        return self._storage.get(user_id)

    def create(self, data: UserCreate) -> dict:
        """Insert a new user and return it."""
        user = {"id": self._next_id, "name": data.name, "email": data.email}
        self._storage[self._next_id] = user
        self._next_id += 1
        return user

    def delete(self, user_id: int) -> bool:
        """Delete a user. Returns True if found, False otherwise."""
        if user_id in self._storage:
            del self._storage[user_id]
            return True
        return False
