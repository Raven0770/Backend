"""
Controller Layer — User Controller

The controller receives validated data from the router,
calls the appropriate service method, and shapes the response.

Think of it as a translator:
  Router speaks "HTTP" → Controller translates → Service speaks "business logic"
"""

from app.models.user import UserCreate, UserResponse, MessageResponse
from app.services.user_service import UserService


class UserController:
    """Translates HTTP-level requests into service calls."""

    def __init__(self, service: UserService) -> None:
        self._service = service

    def list_users(self) -> list[UserResponse]:
        users = self._service.list_users()
        return [UserResponse(**u) for u in users]

    def get_user(self, user_id: int) -> UserResponse:
        user = self._service.get_user(user_id)
        return UserResponse(**user)

    def create_user(self, data: UserCreate) -> UserResponse:
        user = self._service.create_user(data)
        return UserResponse(**user)

    def delete_user(self, user_id: int) -> MessageResponse:
        self._service.delete_user(user_id)
        return MessageResponse(message=f"User {user_id} deleted successfully")
