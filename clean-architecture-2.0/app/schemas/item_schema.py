"""Pydantic schemas for request validation, response serialization, and auth context."""

from datetime import datetime
from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """Represents the authenticated caller attached by AuthMiddleware."""

    username: str
    token: str


class ItemCreate(BaseModel):
    """Payload expected when creating a new item."""

    name: str = Field(..., min_length=1, max_length=100, examples=["Notebook"])
    description: str | None = Field(
        default=None,
        max_length=300,
        examples=["A clean ruled notebook"],
    )


class ItemResponse(BaseModel):
    """Shape of an item returned by the API."""

    id: int
    name: str
    description: str | None = None
    created_by: str
    created_at: datetime


class MessageResponse(BaseModel):
    """Simple envelope used for status or health responses."""

    status: str
    message: str
