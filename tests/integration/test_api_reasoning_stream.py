from __future__ import annotations

from fastapi.testclient import TestClient

from local_model.api.server import create_app
from local_model.models import GenerationDelta


def test_reasoning_and_answer_fragments_are_separated(register_test_manifest, parse_sse_events, monkeypatch) -> None:
    register_test_manifest("reasoning-stream-demo")
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)

    def fake_stream(self, *, request, manifest, decision):
        return iter(
            [
                GenerationDelta(sequence=1, reasoning_delta="step one"),
                GenerationDelta(sequence=2, content_delta="323", finish_reason="stop"),
            ]
        )

    monkeypatch.setattr("local_model.runners.mlx_runner.MLXRunner.stream", fake_stream)

    client = TestClient(create_app())
    with client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "reasoning-stream-demo",
            "stream": True,
            "messages": [{"role": "user", "content": "What is 17 * 19?"}],
        },
    ) as response:
        events = parse_sse_events(list(response.iter_lines()))

    assert events[1]["choices"][0]["delta"]["reasoning_content"] == "step one"
    assert events[2]["choices"][0]["delta"]["content"] == "323"
    assert events[2]["choices"][0]["finish_reason"] == "stop"
