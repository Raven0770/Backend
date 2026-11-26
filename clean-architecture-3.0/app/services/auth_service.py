"""
Service Layer — Auth Service (Business Logic)

Handles register and login logic:
  - Register: check if username exists → hash password → store account → return token.
  - Login: find account → verify password → return token.

This layer uses the AuthRepository for data access and the security
utilities for password hashing and JWT creation.
"""

from fastapi import HTTPException, status

from app.models.auth import RegisterRequest, LoginRequest
from app.repositories.auth_repository import AuthRepository
from app.utils.security import hash_password, verify_password, create_access_token


class AuthService:
    """Business-logic for authentication."""

    def __init__(self, repository: AuthRepository) -> None:
        self._repo = repository

    def register(self, data: RegisterRequest) -> dict:
        """
        Register a new account.

        Business rules:
          - Username must not already exist.
          - Password is hashed before storage (never store plain text!).
          - A JWT token is returned immediately so the user is logged
            in right after registering.
        """
        if self._repo.exists(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{data.username}' is already taken",
            )

        hashed = hash_password(data.password)
        self._repo.create(data.username, hashed)

        # Create a JWT with the username as the "subject" claim
        token = create_access_token({"sub": data.username})
        return {"access_token": token, "message": "Account created successfully"}

    def login(self, data: LoginRequest) -> dict:
        """
        Authenticate a user and return a JWT.

        Business rules:
          - Account must exist.
          - Password must match the stored hash.
        """
        account = self._repo.find_by_username(data.username)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not verify_password(data.password, account["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token = create_access_token({"sub": data.username})
        return {"access_token": token, "message": "Login successful"}
