from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    """Input Resource: validates the JSON body sent by the client."""

    text: str = Field(..., min_length=1, max_length=200, examples=["Hello FastAPI!"])


class MessageResponse(BaseModel):
    """Output Resource: defines the exact JSON shape returned to the client."""

    status: str
    user: str
    message: str
