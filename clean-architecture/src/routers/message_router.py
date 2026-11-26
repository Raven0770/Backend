from fastapi import APIRouter, Depends, Request, status

from src.controllers.message_controller import MessageController
from src.resources.message_resource import MessageCreateRequest, MessageResponse

router = APIRouter(tags=["Messages"])


def get_message_controller() -> MessageController:
    """Dependency provider so the router stays decoupled from instantiation."""
    return MessageController()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    """Public route (skipped by auth middleware) to verify the API is alive."""
    return {
        "status": "ok",
        "message": "FastAPI backend is running.",
    }


@router.get(
    "/api/v1/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def read_message(
    request: Request,
    controller: MessageController = Depends(get_message_controller),
) -> MessageResponse:
    """Protected route: reads the authenticated dummy user and delegates to controller."""
    username = getattr(request.state, "user", "anonymous")
    return controller.get_welcome_message(username=username)


@router.post(
    "/api/v1/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    payload: MessageCreateRequest,
    request: Request,
    controller: MessageController = Depends(get_message_controller),
) -> MessageResponse:
    """Protected route: validates payload via Resource and delegates to controller."""
    username = getattr(request.state, "user", "anonymous")
    return controller.create_message(username=username, payload=payload)
