from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    runtime: str | None = None
    preset: str = "mlx-api"
    fallback_allowed: bool = True
    max_tokens: int = Field(default=256, ge=1, le=4096)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "local-model"
    runtime: str
    turboquant_compatible: bool

