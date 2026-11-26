from fastapi import HTTPException, status

from src.repositories.message_repository import MessageRepository
from src.resources.message_resource import MessageCreateRequest, MessageResponse


class MessageController:
    """
    Controller Layer (Business Logic):
    Coordinates between the Router (HTTP) and the Repository (data).
    It does NOT know about HTTP headers or SQL queries.
    """

    def __init__(self, repository: MessageRepository | None = None) -> None:
        self.repository = repository or MessageRepository()

    def get_welcome_message(self, username: str) -> MessageResponse:
        raw_message = self.repository.get_welcome_message()
        return MessageResponse(
            status="success",
            user=username,
            message=raw_message,
        )

    def create_message(
        self, username: str, payload: MessageCreateRequest
    ) -> MessageResponse:
        cleaned_text = payload.text.strip()
        if not cleaned_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message text cannot be blank.",
            )

        saved_message = self.repository.save_message(
            username=username,
            text=cleaned_text,
        )
        return MessageResponse(
            status="created",
            user=username,
            message=saved_message,
        )
