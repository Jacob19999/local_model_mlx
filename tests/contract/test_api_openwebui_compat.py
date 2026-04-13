from __future__ import annotations

import shutil

from fastapi.testclient import TestClient

from local_model.api.server import create_app
from local_model.downloads import cache_destination_for_alias, reset_destination
from local_model.models import GenerationResult
from local_model.registry import register_manifest


def test_openwebui_compatible_api_exposes_models_and_chat(isolated_repo, valid_model_dir, monkeypatch) -> None:
    destination = cache_destination_for_alias("demo-openwebui")
    reset_destination(destination)
    shutil.copytree(valid_model_dir, destination, dirs_exist_ok=True)
    register_manifest(
        alias="demo-openwebui",
        source_type="local_dir",
        source_location=str(valid_model_dir),
        local_path="models/cache/demo-openwebui",
    )

    monkeypatch.setattr(
        "local_model.api.server.generate_once",
        lambda **_: GenerationResult(
            model_alias="demo-openwebui",
            requested_runtime="mlx",
            active_runtime="mlx",
            output_text="openwebui ok",
            command=["python", "-m", "mlx_lm", "generate"],
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
    assert chat_payload["runtime"]["runtime"] == "mlx"
    assert chat_payload["choices"][0]["message"]["content"] == "openwebui ok"
