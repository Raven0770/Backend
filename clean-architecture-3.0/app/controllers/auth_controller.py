"""
Controller Layer — Auth Controller

Bridges HTTP requests to the AuthService.
Converts service results into Pydantic response models.
"""

from app.models.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService


class AuthController:
    """Translates auth HTTP requests into service calls."""

    def __init__(self, service: AuthService) -> None:
        self._service = service

    def register(self, data: RegisterRequest) -> TokenResponse:
        result = self._service.register(data)
        return TokenResponse(**result)

    def login(self, data: LoginRequest) -> TokenResponse:
        result = self._service.login(data)
        return TokenResponse(**result)
