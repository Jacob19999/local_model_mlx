from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, HTTPException

from local_model.api.schemas import ChatCompletionRequest, ModelCard
from local_model.cli import generate_once
from local_model.registry import get_manifest, list_manifests
from local_model.services.diagnostics import render_manifest_summary


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
            )
            for manifest in list_manifests()
            if manifest.api_visible
        ]
        return {"data": payload}

    @app.post("/v1/chat/completions")
    def chat_completions(request: ChatCompletionRequest) -> dict[str, object]:
        try:
            manifest = get_manifest(request.model)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        prompt = "\n".join(message.content for message in request.messages if message.role != "assistant")
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

        created = int(time.time())
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": created,
            "model": manifest.alias,
            "runtime": render_manifest_summary(manifest),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result.output_text,
                    },
                    "finish_reason": "stop",
                }
            ],
        }

    return app

