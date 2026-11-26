"""
Service Layer (Business Logic) — User Service

This layer sits between the controller and the repository.
It holds the business rules.  For example:
  - "Don't allow duplicate emails"
  - "An admin can delete, but a regular user cannot"

Right now the rules are simple, but as the app grows you add
logic HERE — not in the router and not in the repository.
"""

from fastapi import HTTPException, status

from app.models.user import UserCreate
from app.repositories.user_repository import UserRepository


class UserService:
    """Business-logic operations for users."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def list_users(self) -> list[dict]:
        """Return all users."""
        return self._repo.get_all()

    def get_user(self, user_id: int) -> dict:
        """Return one user or raise 404."""
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return user

    def create_user(self, data: UserCreate) -> dict:
        """
        Create a user after checking business rules.
        Rule: email must not already exist.
        """
        existing = self._repo.get_all()
        for u in existing:
            if u["email"] == data.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{data.email}' is already taken",
                )
        return self._repo.create(data)

    def delete_user(self, user_id: int) -> None:
        """Delete a user or raise 404."""
        deleted = self._repo.delete(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
