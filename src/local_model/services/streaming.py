from __future__ import annotations

import json
from typing import Any

from local_model.models import GenerationDelta


def build_chat_completion_chunk(
    *,
    request_id: str,
    created: int,
    model: str,
    delta: GenerationDelta,
) -> dict[str, Any]:
    payload_delta: dict[str, Any] = {}
    if delta.role:
        payload_delta["role"] = delta.role
    if delta.content_delta:
        payload_delta["content"] = delta.content_delta
    if delta.reasoning_delta:
        payload_delta["reasoning_content"] = delta.reasoning_delta
    return {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": payload_delta,
                "finish_reason": delta.finish_reason,
            }
        ],
    }


def serialize_sse_event(payload: dict[str, Any] | str) -> str:
    data = payload if isinstance(payload, str) else json.dumps(payload, separators=(",", ":"))
    return f"data: {data}\n\n"


def serialize_done_event() -> str:
    return serialize_sse_event("[DONE]")
