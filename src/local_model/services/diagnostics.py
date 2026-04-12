from __future__ import annotations

from local_model.models import ModelManifest, RuntimeDecision


def render_runtime_banner(manifest: ModelManifest, decision: RuntimeDecision) -> list[str]:
    lines = [
        f"model: {manifest.alias}",
        f"requested_runtime: {decision.requested_runtime}",
        f"active_runtime: {decision.active_runtime}",
    ]
    if decision.fallback_used and decision.fallback_reason:
        lines.append(f"fallback: {decision.fallback_reason}")
    lines.extend(decision.notices)
    return lines


def render_manifest_summary(manifest: ModelManifest) -> dict[str, object]:
    return {
        "alias": manifest.alias,
        "display_name": manifest.display_name,
        "source_type": manifest.source.type,
        "source": manifest.source.location,
        "local_path": manifest.local_path,
        "default_preset": manifest.default_preset,
        "supported_runtimes": manifest.supported_runtimes,
        "turboquant_compatible": manifest.turboquant_compatible,
        "api_visible": manifest.api_visible,
        "tags": manifest.tags,
    }

