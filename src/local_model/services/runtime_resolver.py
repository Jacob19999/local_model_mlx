from __future__ import annotations

import importlib.util
import os

from local_model.models import ModelManifest, RuntimeCapabilityProfile, RuntimeDecision, RuntimePreset


def _turbo_available() -> bool:
    return bool(os.environ.get("LOCAL_MODEL_TURBO_COMMAND")) or importlib.util.find_spec("mlx_turboquant") is not None


def _mlx_available() -> bool:
    return importlib.util.find_spec("mlx_lm") is not None


def _resolve_capabilities(
    *,
    manifest: ModelManifest,
    preset: RuntimePreset,
    active_runtime: str,
) -> RuntimeCapabilityProfile:
    supports_streaming = manifest.capabilities.supports_streaming or preset.capabilities.supports_streaming
    reasoning_format = (
        preset.capabilities.reasoning_format
        if preset.capabilities.reasoning_format != "none"
        else manifest.capabilities.reasoning_format
    )
    reasoning_enabled_by_default = (
        manifest.capabilities.reasoning_enabled_by_default or preset.capabilities.reasoning_enabled_by_default
    )

    if active_runtime != "mlx":
        supports_streaming = False
        reasoning_format = "none"
        reasoning_enabled_by_default = False

    return RuntimeCapabilityProfile(
        supports_streaming=supports_streaming,
        reasoning_format=reasoning_format,
        reasoning_enabled_by_default=reasoning_enabled_by_default,
    )


def resolve_runtime(
    *,
    manifest: ModelManifest,
    preset: RuntimePreset,
    requested_runtime: str | None = None,
    fallback_allowed: bool | None = None,
    stream: bool = False,
) -> RuntimeDecision:
    target_runtime = requested_runtime or preset.runtime
    allow_fallback = preset.allow_fallback if fallback_allowed is None else fallback_allowed
    notices: list[str] = []

    if target_runtime not in manifest.supported_runtimes:
        reason = f"Manifest runtime list excludes `{target_runtime}`."
        if allow_fallback and manifest.runtime in manifest.supported_runtimes:
            notices.append(
                f"{target_runtime} requested, but the manifest excludes it; falling back to {manifest.runtime}."
            )
            return RuntimeDecision(
                requested_runtime=target_runtime,
                active_runtime=manifest.runtime,
                fallback_used=True,
                fallback_reason=reason,
                notices=notices,
                streaming_requested=stream,
                capabilities=_resolve_capabilities(manifest=manifest, preset=preset, active_runtime=manifest.runtime),
            )
        raise RuntimeError(reason)

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
                    streaming_requested=stream,
                    capabilities=_resolve_capabilities(manifest=manifest, preset=preset, active_runtime="mlx"),
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
                    streaming_requested=stream,
                    capabilities=_resolve_capabilities(manifest=manifest, preset=preset, active_runtime="mlx"),
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
                    streaming_requested=stream,
                    capabilities=_resolve_capabilities(manifest=manifest, preset=preset, active_runtime="mlx"),
                )
            raise RuntimeError(reason)

    if target_runtime == "mlx" and not _mlx_available():
        raise RuntimeError("Stock MLX runtime is unavailable on this machine.")

    capabilities = _resolve_capabilities(manifest=manifest, preset=preset, active_runtime=target_runtime)
    if stream and not capabilities.supports_streaming:
        reason = f"Runtime `{target_runtime}` cannot satisfy incremental streaming for `{manifest.alias}`."
        fallback_runtime = manifest.runtime
        fallback_capabilities = _resolve_capabilities(manifest=manifest, preset=preset, active_runtime=fallback_runtime)
        if allow_fallback and fallback_runtime != target_runtime and fallback_capabilities.supports_streaming:
            notices.append(
                f"{target_runtime} requested for a streamed request, but it cannot stream incrementally; "
                f"falling back to {fallback_runtime}."
            )
            return RuntimeDecision(
                requested_runtime=target_runtime,
                active_runtime=fallback_runtime,
                fallback_used=True,
                fallback_reason=reason,
                notices=notices,
                streaming_requested=stream,
                capabilities=fallback_capabilities,
            )
        raise RuntimeError(reason)

    return RuntimeDecision(
        requested_runtime=target_runtime,
        active_runtime=target_runtime,
        fallback_used=False,
        notices=notices,
        streaming_requested=stream,
        capabilities=capabilities,
    )
