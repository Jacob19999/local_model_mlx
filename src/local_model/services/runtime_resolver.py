from __future__ import annotations

import importlib.util
import os

from local_model.models import ModelManifest, RuntimeDecision, RuntimePreset


def _turbo_available() -> bool:
    return bool(os.environ.get("LOCAL_MODEL_TURBO_COMMAND")) or importlib.util.find_spec("mlx_turboquant") is not None


def resolve_runtime(
    *,
    manifest: ModelManifest,
    preset: RuntimePreset,
    requested_runtime: str | None = None,
    fallback_allowed: bool | None = None,
) -> RuntimeDecision:
    target_runtime = requested_runtime or preset.runtime
    allow_fallback = preset.allow_fallback if fallback_allowed is None else fallback_allowed
    notices: list[str] = []

    if target_runtime == "turboquant":
        if not manifest.turboquant_compatible:
            reason = "Manifest does not declare TurboQuant compatibility."
            if allow_fallback:
                notices.append("TurboQuant requested, but the manifest is not compatible; falling back to stock MLX.")
                return RuntimeDecision(
                    requested_runtime="turboquant",
                    active_runtime="mlx",
                    fallback_used=True,
                    fallback_reason=reason,
                    notices=notices,
                )
            raise RuntimeError(reason)

        if "turboquant" not in manifest.supported_runtimes:
            reason = "Manifest runtime list excludes TurboQuant."
            if allow_fallback:
                notices.append("TurboQuant requested, but the runtime list excludes it; falling back to stock MLX.")
                return RuntimeDecision(
                    requested_runtime="turboquant",
                    active_runtime="mlx",
                    fallback_used=True,
                    fallback_reason=reason,
                    notices=notices,
                )
            raise RuntimeError(reason)

        if not _turbo_available():
            reason = "TurboQuant runtime is unavailable on this machine."
            if allow_fallback:
                notices.append("TurboQuant runtime unavailable; falling back to stock MLX.")
                return RuntimeDecision(
                    requested_runtime="turboquant",
                    active_runtime="mlx",
                    fallback_used=True,
                    fallback_reason=reason,
                    notices=notices,
                )
            raise RuntimeError(reason)

    return RuntimeDecision(
        requested_runtime=target_runtime,
        active_runtime=target_runtime,
        fallback_used=False,
        notices=notices,
    )

