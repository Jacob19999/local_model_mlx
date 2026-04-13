from __future__ import annotations

from fastapi.testclient import TestClient

from local_model.api.server import create_app
from local_model.models import GenerationDelta, GenerationResult, RuntimeCapabilityProfile, RuntimeDecision


def test_non_stream_reasoning_is_separate_from_answer(register_test_manifest, monkeypatch) -> None:
    manifest = register_test_manifest("reasoning-demo")

    monkeypatch.setattr(
        "local_model.api.server.generate_once",
        lambda **_: GenerationResult(
            model_alias=manifest.alias,
            requested_runtime="mlx",
            active_runtime="mlx",
            output_text="42",
            reasoning_text="17 * 19 = 323, so revise to 42 for the fixture",
            finish_reason="stop",
            capabilities=RuntimeCapabilityProfile(
                supports_streaming=True,
                reasoning_format="think_tags",
                reasoning_enabled_by_default=True,
            ),
        ),
    )

    client = TestClient(create_app())
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "reasoning-demo",
            "messages": [{"role": "user", "content": "What is 17 * 19?"}],
        },
    )

    payload = response.json()
    assert payload["choices"][0]["message"]["content"] == "42"
    assert payload["choices"][0]["message"]["reasoning_content"] == "17 * 19 = 323, so revise to 42 for the fixture"


def test_stream_reasoning_uses_reasoning_content_field(register_test_manifest, parse_sse_events, monkeypatch) -> None:
    manifest = register_test_manifest("reasoning-demo")

    monkeypatch.setattr(
        "local_model.api.server.stream_once",
        lambda **_: (
            manifest,
            RuntimeDecision(
                requested_runtime="mlx",
                active_runtime="mlx",
                fallback_used=False,
                streaming_requested=True,
                capabilities=RuntimeCapabilityProfile(
                    supports_streaming=True,
                    reasoning_format="think_tags",
                    reasoning_enabled_by_default=True,
                ),
            ),
            iter(
                [
                    GenerationDelta(sequence=1, reasoning_delta="step one"),
                    GenerationDelta(sequence=2, content_delta="42", finish_reason="stop"),
                ]
            ),
        ),
    )

    client = TestClient(create_app())
    with client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "reasoning-demo",
            "stream": True,
            "messages": [{"role": "user", "content": "What is 17 * 19?"}],
        },
    ) as response:
        events = parse_sse_events(list(response.iter_lines()))

    assert events[1]["choices"][0]["delta"]["reasoning_content"] == "step one"
    assert events[2]["choices"][0]["delta"]["content"] == "42"
    assert events[2]["choices"][0]["finish_reason"] == "stop"
