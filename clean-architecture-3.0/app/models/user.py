"""
Resource Layer — User Models

This file defines the "shape" of data that flows through the application.
These are Pydantic models (not database models). They validate incoming
request data and structure outgoing response data.

Pydantic comes bundled with FastAPI — no extra install needed.
"""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for creating a new user (request body)."""

    name: str = Field(..., min_length=1, max_length=100, examples=["Alice"])
    email: str = Field(..., examples=["alice@example.com"])


class UserResponse(BaseModel):
    """Schema for returning a user (response body)."""

    id: int
    name: str
    email: str


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
