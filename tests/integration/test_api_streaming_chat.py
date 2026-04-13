from __future__ import annotations

from fastapi.testclient import TestClient

from local_model.api.server import create_app
from local_model.models import GenerationDelta


def test_streamed_chat_emits_ordered_chunks_before_done(register_test_manifest, parse_sse_events, monkeypatch) -> None:
    register_test_manifest("stream-demo")
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)

    def fake_stream(self, *, request, manifest, decision):
        return iter(
            [
                GenerationDelta(sequence=1, content_delta="one "),
                GenerationDelta(sequence=2, content_delta="two "),
                GenerationDelta(sequence=3, content_delta="three", finish_reason="stop"),
            ]
        )

    monkeypatch.setattr("local_model.runners.mlx_runner.MLXRunner.stream", fake_stream)

    client = TestClient(create_app())
    with client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "stream-demo",
            "stream": True,
            "messages": [{"role": "user", "content": "Count to three"}],
        },
    ) as response:
        events = parse_sse_events(list(response.iter_lines()))

    assert events[0]["choices"][0]["delta"]["role"] == "assistant"
    assert events[1]["choices"][0]["delta"]["content"] == "one "
    assert events[2]["choices"][0]["delta"]["content"] == "two "
    assert events[3]["choices"][0]["delta"]["content"] == "three"
    assert events[3]["choices"][0]["finish_reason"] == "stop"
    assert events[4] == "[DONE]"


def test_non_stream_chat_still_returns_single_completion(register_test_manifest, monkeypatch) -> None:
    register_test_manifest("stream-demo")
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)

    def fake_generate(self, *, request, manifest, decision):
        return iter(
            [
                GenerationDelta(sequence=1, content_delta="single ", finish_reason=None),
                GenerationDelta(sequence=2, content_delta="response", finish_reason="stop"),
            ]
        )

    monkeypatch.setattr("local_model.runners.mlx_runner.MLXRunner.stream", fake_generate)

    client = TestClient(create_app())
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "stream-demo",
            "messages": [{"role": "user", "content": "Say hello"}],
        },
    )

    payload = response.json()
    assert payload["object"] == "chat.completion"
    assert payload["choices"][0]["message"]["content"] == "single response"
    assert payload["choices"][0]["finish_reason"] == "stop"
