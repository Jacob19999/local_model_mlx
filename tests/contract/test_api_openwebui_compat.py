from __future__ import annotations

from fastapi.testclient import TestClient

from local_model.api.server import create_app
from local_model.models import GenerationDelta, GenerationResult, RuntimeCapabilityProfile, RuntimeDecision


def test_openwebui_compatible_api_exposes_models_and_non_stream_chat(register_test_manifest, monkeypatch) -> None:
    manifest = register_test_manifest("demo-openwebui")

    monkeypatch.setattr(
        "local_model.api.server.generate_once",
        lambda **_: GenerationResult(
            model_alias=manifest.alias,
            requested_runtime="mlx",
            active_runtime="mlx",
            output_text="openwebui ok",
            finish_reason="stop",
            capabilities=RuntimeCapabilityProfile(
                supports_streaming=True,
                reasoning_format="think_tags",
                reasoning_enabled_by_default=True,
            ),
        ),
    )

    client = TestClient(create_app())

    models_response = client.get("/v1/models")
    assert models_response.status_code == 200
    models_payload = models_response.json()
    assert models_payload["data"] == [
        {
            "id": "demo-openwebui",
            "object": "model",
            "owned_by": "local-model",
            "runtime": "mlx",
            "turboquant_compatible": False,
            "default_preset": "mlx-chat",
            "supported_runtimes": ["mlx"],
            "supports_streaming": False,
            "reasoning_format": "none",
            "reasoning_enabled_by_default": False,
        }
    ]

    chat_response = client.post(
        "/v1/chat/completions",
        json={
            "model": "demo-openwebui",
            "messages": [{"role": "user", "content": "Hello from Open WebUI"}],
        },
    )
    assert chat_response.status_code == 200
    chat_payload = chat_response.json()
    assert chat_payload["object"] == "chat.completion"
    assert chat_payload["model"] == "demo-openwebui"
    assert chat_payload["runtime"]["active_runtime"] == "mlx"
    assert chat_payload["choices"][0]["message"]["content"] == "openwebui ok"
    assert chat_payload["choices"][0]["finish_reason"] == "stop"


def test_openwebui_compatible_api_streams_ordered_chunks(register_test_manifest, parse_sse_events, monkeypatch) -> None:
    manifest = register_test_manifest("demo-openwebui")

    monkeypatch.setattr(
        "local_model.api.server.stream_once",
        lambda **_: (
            manifest,
            RuntimeDecision(
                requested_runtime="mlx",
                active_runtime="mlx",
                fallback_used=False,
                streaming_requested=True,
                capabilities=RuntimeCapabilityProfile(supports_streaming=True),
            ),
            iter(
                [
                    GenerationDelta(sequence=1, content_delta="Hello "),
                    GenerationDelta(sequence=2, content_delta="world", finish_reason="stop"),
                ]
            ),
        ),
    )

    client = TestClient(create_app())

    with client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "demo-openwebui",
            "stream": True,
            "messages": [{"role": "user", "content": "Hello from Open WebUI"}],
        },
    ) as response:
        assert response.status_code == 200
        events = parse_sse_events(list(response.iter_lines()))

    assert events[0]["object"] == "chat.completion.chunk"
    assert events[0]["choices"][0]["delta"]["role"] == "assistant"
    assert events[1]["choices"][0]["delta"]["content"] == "Hello "
    assert events[2]["choices"][0]["delta"]["content"] == "world"
    assert events[2]["choices"][0]["finish_reason"] == "stop"
    assert events[3] == "[DONE]"
