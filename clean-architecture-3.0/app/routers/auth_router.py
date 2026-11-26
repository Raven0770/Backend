"""
Router Layer — Auth Router

Public endpoints for user registration and login.
These do NOT require authentication (you can't log in if you're
already required to be logged in!).
"""

from fastapi import APIRouter, status

from app.controllers.auth_controller import AuthController
from app.models.auth import RegisterRequest, LoginRequest, TokenResponse
from app.repositories.auth_repository import AuthRepository
from app.services.auth_service import AuthService

# --- Wire the dependency chain ---
_repository = AuthRepository()
_service = AuthService(_repository)
_controller = AuthController(_service)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    """Register a new account. Returns a JWT token."""
    return _controller.register(body)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(body: LoginRequest):
    """Log in with username and password. Returns a JWT token."""
    return _controller.login(body)
