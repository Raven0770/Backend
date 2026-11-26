"""
Resource Layer — Auth Models

Pydantic schemas for authentication: register, login, and token responses.
These models validate the shape of auth-related request and response data.
"""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Data required to register a new account."""

    username: str = Field(..., min_length=3, max_length=50, examples=["alice"])
    password: str = Field(..., min_length=6, examples=["secret123"])


class LoginRequest(BaseModel):
    """Data required to log in."""

    username: str = Field(..., examples=["alice"])
    password: str = Field(..., examples=["secret123"])


class TokenResponse(BaseModel):
    """Returned after a successful login or register."""

    access_token: str
    token_type: str = "bearer"
    message: str
