from __future__ import annotations

import pytest

from local_model.models import ModelManifest, ModelSource, RuntimePreset
from local_model.services.runtime_resolver import resolve_runtime


def _manifest() -> ModelManifest:
    return ModelManifest(
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
        tags=["text-generation", "nemotron", "mlx"],
    )


def test_unsupported_turbo_runtime_fails_without_fallback(monkeypatch) -> None:
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)

    with pytest.raises(RuntimeError, match="excludes `turboquant`"):
        resolve_runtime(
            manifest=_manifest(),
            preset=RuntimePreset(name="mlx-chat", runtime="mlx", description="Stock MLX"),
            requested_runtime="turboquant",
            fallback_allowed=False,
        )


def test_unsupported_turbo_runtime_falls_back_to_mlx(monkeypatch) -> None:
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)

    decision = resolve_runtime(
        manifest=_manifest(),
        preset=RuntimePreset(name="mlx-turbo", runtime="turboquant", description="Turbo", allow_fallback=True),
        requested_runtime="turboquant",
        fallback_allowed=True,
    )

    assert decision.active_runtime == "mlx"
    assert decision.fallback_used is True
    assert "falling back to mlx" in decision.notices[0].lower()
