from __future__ import annotations

import subprocess

from local_model.models import ExecutionRequest, ModelManifest, ModelSource, RuntimeDecision
from local_model.runners.mlx_runner import MLXRunner


def test_mlx_runner_uses_supported_cli_and_returns_clean_stdout(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(command, check, capture_output, text):
        captured["command"] = command
        assert check is True
        assert capture_output is True
        assert text is True
        return subprocess.CompletedProcess(command, 0, stdout="OK\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = MLXRunner().generate(
        request=ExecutionRequest(
            model_alias="nemotron-3-nano-30b-a3b",
            prompt="Reply with OK.",
            preset_name="mlx-chat",
            requested_runtime="mlx",
            fallback_allowed=False,
            source="test",
            max_tokens=16,
            temperature=0.0,
        ),
        manifest=ModelManifest(
            alias="nemotron-3-nano-30b-a3b",
            display_name="Install Nemotron 3 Nano 30B A3B",
            source=ModelSource(
                type="hf_repo",
                location="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
            ),
            local_path="models/cache/nemotron-3-nano-30b-a3b",
            default_preset="mlx-chat",
            runtime="mlx",
            supported_runtimes=["mlx"],
            turboquant_compatible=False,
        ),
        decision=RuntimeDecision(
            requested_runtime="mlx",
            active_runtime="mlx",
            fallback_used=False,
        ),
    )

    command = captured["command"]
    assert command[:4] == [command[0], "-m", "mlx_lm", "generate"]
    assert "--verbose" in command
    assert "false" in command
    assert result.output_text == "OK"
