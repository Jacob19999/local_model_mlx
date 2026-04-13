from __future__ import annotations

import time
import uuid
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from local_model.api.schemas import ChatCompletionRequest, ModelCard
from local_model.cli import generate_once, stream_once
from local_model.models import GenerationDelta, RuntimeDecision
from local_model.registry import get_manifest, list_manifests
from local_model.services.diagnostics import render_runtime_summary
from local_model.services.streaming import build_chat_completion_chunk, serialize_done_event, serialize_sse_event


def _prompt_from_messages(request: ChatCompletionRequest) -> str:
    return "\n".join(message.content for message in request.messages if message.role != "assistant")


def _stream_events(
    *,
    request_id: str,
    created: int,
    model: str,
    deltas: Iterator[GenerationDelta],
) -> Iterator[str]:
    yield serialize_sse_event(
        build_chat_completion_chunk(
            request_id=request_id,
            created=created,
            model=model,
            delta=GenerationDelta(sequence=0, role="assistant"),
        )
    )
    try:
        for delta in deltas:
            yield serialize_sse_event(
                build_chat_completion_chunk(
                    request_id=request_id,
                    created=created,
                    model=model,
                    delta=delta,
                )
            )
    except Exception:
        return
    yield serialize_done_event()


def create_app() -> FastAPI:
    app = FastAPI(title="Local Model API", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "registered_models": len(list_manifests()),
        }

    @app.get("/v1/models")
    def models() -> dict[str, list[ModelCard]]:
        payload = [
            ModelCard(
                id=manifest.alias,
                runtime=manifest.runtime,
                turboquant_compatible=manifest.turboquant_compatible,
                default_preset=manifest.default_preset,
                supported_runtimes=manifest.supported_runtimes,
                supports_streaming=manifest.capabilities.supports_streaming,
                reasoning_format=manifest.capabilities.reasoning_format,
                reasoning_enabled_by_default=manifest.capabilities.reasoning_enabled_by_default,
            )
            for manifest in list_manifests()
            if manifest.api_visible
        ]
        return {"data": payload}

    @app.post("/v1/chat/completions")
    def chat_completions(request: ChatCompletionRequest):
        try:
            manifest = get_manifest(request.model)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        prompt = _prompt_from_messages(request)
        request_id = f"chatcmpl-{uuid.uuid4().hex}"
        created = int(time.time())

        if request.stream:
            try:
                stream_manifest, _, deltas = stream_once(
                    model_alias=manifest.alias,
                    prompt=prompt,
                    preset_name=request.preset,
                    requested_runtime=request.runtime,
                    fallback_allowed=request.fallback_allowed,
                    source="api",
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                )
            except Exception as exc:  # pragma: no cover - surfaced as API error
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            return StreamingResponse(
                _stream_events(
                    request_id=request_id,
                    created=created,
                    model=stream_manifest.alias,
                    deltas=deltas,
                ),
                media_type="text/event-stream",
            )

        try:
            result = generate_once(
                model_alias=manifest.alias,
                prompt=prompt,
                preset_name=request.preset,
                requested_runtime=request.runtime,
                fallback_allowed=request.fallback_allowed,
                source="api",
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        except Exception as exc:  # pragma: no cover - surfaced as API error
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return {
            "id": request_id,
            "object": "chat.completion",
            "created": created,
            "model": manifest.alias,
            "runtime": render_runtime_summary(
                manifest,
                RuntimeDecision(
                    requested_runtime=result.requested_runtime,
                    active_runtime=result.active_runtime,
                    fallback_used=bool(result.fallback_reason),
                    fallback_reason=result.fallback_reason,
                    notices=result.notices,
                    capabilities=result.capabilities,
                ),
            ),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result.output_text,
                        "reasoning_content": result.reasoning_text or None,
                    },
                    "finish_reason": result.finish_reason,
                }
            ],
        }

    return app
