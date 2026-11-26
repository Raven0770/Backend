"""Minimal application configuration without heavy external settings libraries."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Static configuration for the application.

    Tomorrow, when you add a database, you can add `database_url` here
    and read it from an environment variable.
    """

    app_name: str = "FastAPI Layered Architecture Demo"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    # Dummy token -> user mapping for learning middleware authentication.
    # In production, replace this with JWT verification or an auth provider.
    dummy_tokens: dict[str, str] | None = None
    public_paths: tuple[str, ...] = (
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    )

    def get_tokens(self) -> dict[str, str]:
        """Return valid dummy tokens mapped to usernames."""
        if self.dummy_tokens is not None:
            return self.dummy_tokens
        default_token = os.getenv("DEMO_AUTH_TOKEN", "demo-secret-token")
        return {
            default_token: "demo-user",
            "admin-secret-token": "admin-user",
        }


settings = Settings()
