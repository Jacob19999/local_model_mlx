from __future__ import annotations

import pytest

from local_model.models import ModelManifest, ModelSource, RuntimeCapabilityProfile, RuntimePreset
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
        default_preset="mlx-api-reasoning",
        runtime="mlx",
        supported_runtimes=["mlx", "turboquant"],
        turboquant_compatible=True,
        tags=["text-generation", "nemotron", "mlx"],
        capabilities=RuntimeCapabilityProfile(
            supports_streaming=True,
            reasoning_format="think_tags",
            reasoning_enabled_by_default=True,
        ),
    )


def test_unsupported_streamed_runtime_fails_without_fallback(monkeypatch) -> None:
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)
    monkeypatch.setattr("local_model.services.runtime_resolver._turbo_available", lambda: True)

    with pytest.raises(RuntimeError, match="cannot satisfy incremental streaming"):
        resolve_runtime(
            manifest=_manifest(),
            preset=RuntimePreset(name="mlx-turbo", runtime="turboquant", description="Turbo", allow_fallback=False),
            requested_runtime="turboquant",
            fallback_allowed=False,
            stream=True,
        )


def test_streamed_runtime_falls_back_to_mlx_when_requested_runtime_cannot_stream(monkeypatch) -> None:
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)
    monkeypatch.setattr("local_model.services.runtime_resolver._turbo_available", lambda: True)

    decision = resolve_runtime(
        manifest=_manifest(),
        preset=RuntimePreset(name="mlx-turbo", runtime="turboquant", description="Turbo", allow_fallback=True),
        requested_runtime="turboquant",
        fallback_allowed=True,
        stream=True,
    )

    assert decision.active_runtime == "mlx"
    assert decision.fallback_used is True
    assert decision.capabilities.supports_streaming is True
    assert "falling back to mlx" in decision.notices[-1].lower()


def test_mlx_streaming_inherits_reasoning_capabilities(monkeypatch) -> None:
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)

    decision = resolve_runtime(
        manifest=_manifest(),
        preset=RuntimePreset(
            name="mlx-api-reasoning",
            runtime="mlx",
            description="API reasoning",
            capabilities=RuntimeCapabilityProfile(
                supports_streaming=True,
                reasoning_format="think_tags",
                reasoning_enabled_by_default=True,
            ),
        ),
        requested_runtime="mlx",
        fallback_allowed=False,
        stream=True,
    )

    assert decision.active_runtime == "mlx"
    assert decision.capabilities.supports_streaming is True
    assert decision.capabilities.reasoning_format == "think_tags"
