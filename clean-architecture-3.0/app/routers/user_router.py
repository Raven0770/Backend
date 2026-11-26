"""
Router Layer — User Router

The router is the entry gate of your API. It:
  1. Defines URL paths (endpoints) and HTTP methods (GET, POST, DELETE …).
  2. Uses FastAPI's APIRouter to group related routes.
  3. Delegates ALL work to the controller — the router itself does NO logic.

Think of it as a receptionist: it receives the request, checks the form
(path/query params, body), and hands it to the right person (controller).
"""

from fastapi import APIRouter, status

from app.controllers.user_controller import UserController
from app.models.user import MessageResponse, UserCreate, UserResponse

# The controller (and its dependencies) are created once and shared
# across all requests. In a real app you'd use FastAPI's Depends() for
# dependency injection — but for learning, explicit wiring is clearer.
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

_repository = UserRepository()
_service = UserService(_repository)
_controller = UserController(_service)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
def list_users():
    """Get all users."""
    return _controller.list_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """Get a single user by ID."""
    return _controller.get_user(user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate):
    """Create a new user."""
    return _controller.create_user(body)


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int):
    """Delete a user by ID."""
    return _controller.delete_user(user_id)
