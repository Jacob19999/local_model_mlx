from __future__ import annotations

import shutil

from fastapi.testclient import TestClient

from local_model.api.server import create_app
from local_model.downloads import cache_destination_for_alias, reset_destination
from local_model.models import GenerationResult
from local_model.registry import register_manifest


def test_api_exposes_nemotron_model_and_chat(isolated_repo, valid_model_dir, monkeypatch) -> None:
    destination = cache_destination_for_alias("nemotron-3-nano-30b-a3b")
    reset_destination(destination)
    shutil.copytree(valid_model_dir, destination, dirs_exist_ok=True)
    register_manifest(
        alias="nemotron-3-nano-30b-a3b",
        source_type="hf_repo",
        source_location="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        local_path="models/cache/nemotron-3-nano-30b-a3b",
    )

    monkeypatch.setattr(
        "local_model.api.server.generate_once",
        lambda **_: GenerationResult(
            model_alias="nemotron-3-nano-30b-a3b",
            requested_runtime="mlx",
            active_runtime="mlx",
            output_text="api ok",
            command=["python", "-m", "mlx_lm", "generate"],
        ),
    )

    client = TestClient(create_app())

    models_response = client.get("/v1/models")
    assert models_response.status_code == 200
    models_payload = models_response.json()
    assert models_payload["data"][0]["id"] == "nemotron-3-nano-30b-a3b"
    assert models_payload["data"][0]["runtime"] == "mlx"

    chat_response = client.post(
        "/v1/chat/completions",
        json={
            "model": "nemotron-3-nano-30b-a3b",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )
    assert chat_response.status_code == 200
    chat_payload = chat_response.json()
    assert chat_payload["model"] == "nemotron-3-nano-30b-a3b"
    assert chat_payload["runtime"]["runtime"] == "mlx"
    assert chat_payload["choices"][0]["message"]["content"] == "api ok"
