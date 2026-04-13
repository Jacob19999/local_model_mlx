from __future__ import annotations

import json
import shutil

from local_model.cli import generate_once, main
from local_model.downloads import cache_destination_for_alias, reset_destination
from local_model.models import GenerationResult
from local_model.registry import register_manifest


def test_nemotron_is_discoverable_and_runs_on_stock_mlx(isolated_repo, valid_model_dir, monkeypatch, capsys) -> None:
    destination = cache_destination_for_alias("nemotron-3-nano-30b-a3b")
    reset_destination(destination)
    shutil.copytree(valid_model_dir, destination, dirs_exist_ok=True)
    register_manifest(
        alias="nemotron-3-nano-30b-a3b",
        source_type="hf_repo",
        source_location="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        local_path="models/cache/nemotron-3-nano-30b-a3b",
    )

    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)

    def fake_generate(self, *, request, manifest, decision):
        return GenerationResult(
            model_alias=manifest.alias,
            requested_runtime=request.requested_runtime,
            active_runtime=decision.active_runtime,
            output_text="Nemotron loaded successfully.",
            command=["python", "-m", "mlx_lm", "generate"],
            fallback_reason=decision.fallback_reason,
        )

    monkeypatch.setattr("local_model.runners.mlx_runner.MLXRunner.generate", fake_generate)

    assert main(["list-models", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["models"][0]["alias"] == "nemotron-3-nano-30b-a3b"
    assert payload["models"][0]["runtime"] == "mlx"

    result = generate_once(
        model_alias="nemotron-3-nano-30b-a3b",
        prompt="Say hello",
        preset_name="mlx-chat",
        requested_runtime="mlx",
        fallback_allowed=False,
        source="integration-test",
        max_tokens=32,
        temperature=0.2,
    )
    assert result.active_runtime == "mlx"
    assert result.output_text == "Nemotron loaded successfully."
