"""
Repository Layer — Auth Repository

Stores registered user accounts (username + hashed password) in memory.
Tomorrow you can swap this with a real database table — nothing else changes.
"""


class AuthRepository:
    """Data access for registered accounts."""

    def __init__(self) -> None:
        # In-memory store: { "alice": {"username": "alice", "hashed_password": "..."} }
        self._accounts: dict[str, dict] = {}

    def find_by_username(self, username: str) -> dict | None:
        """Return an account dict or None."""
        return self._accounts.get(username)

    def create(self, username: str, hashed_password: str) -> dict:
        """Store a new account and return it."""
        account = {
            "username": username,
            "hashed_password": hashed_password,
        }
        self._accounts[username] = account
        return account

    def exists(self, username: str) -> bool:
        """Check if a username is already taken."""
        return username in self._accounts
