from __future__ import annotations

from fastapi.testclient import TestClient

from local_model.api.server import create_app


def test_api_exposes_nemotron_capability_hints(register_test_manifest) -> None:
    register_test_manifest("nemotron-3-nano-30b-a3b")

    client = TestClient(create_app())

    models_response = client.get("/v1/models")
    assert models_response.status_code == 200
    model = models_response.json()["data"][0]

    assert model["id"] == "nemotron-3-nano-30b-a3b"
    assert model["runtime"] == "mlx"
    assert model["supports_streaming"] is True
    assert model["reasoning_format"] == "think_tags"
    assert model["reasoning_enabled_by_default"] is True
