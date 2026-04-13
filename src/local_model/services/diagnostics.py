from __future__ import annotations

from local_model.models import DiagnosticCheck, ModelManifest, RuntimeDecision
from local_model.registry import inspect_manifests


def render_runtime_banner(manifest: ModelManifest, decision: RuntimeDecision) -> list[str]:
    lines = [
        f"model: {manifest.alias}",
        f"requested_runtime: {decision.requested_runtime}",
        f"active_runtime: {decision.active_runtime}",
        f"streaming_requested: {'yes' if decision.streaming_requested else 'no'}",
        f"supports_streaming: {'yes' if decision.capabilities.supports_streaming else 'no'}",
        f"reasoning_format: {decision.capabilities.reasoning_format}",
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
        "runtime": manifest.runtime,
        "supported_runtimes": manifest.supported_runtimes,
        "turboquant_compatible": manifest.turboquant_compatible,
        "api_visible": manifest.api_visible,
        "tags": manifest.tags,
        "notes": manifest.notes,
        "capabilities": manifest.capabilities.to_dict(),
    }


def render_runtime_summary(manifest: ModelManifest, decision: RuntimeDecision) -> dict[str, object]:
    return {
        "model": manifest.alias,
        "requested_runtime": decision.requested_runtime,
        "active_runtime": decision.active_runtime,
        "fallback_used": decision.fallback_used,
        "fallback_reason": decision.fallback_reason,
        "notices": decision.notices,
        "capabilities": decision.capabilities.to_dict(),
    }


def collect_manifest_checks() -> list[DiagnosticCheck]:
    records = inspect_manifests()
    if not records:
        return [DiagnosticCheck("manifest_health", "pass", "No registered manifests.")]

    invalid = [record for record in records if record["error"]]
    if not invalid:
        return [DiagnosticCheck("manifest_health", "pass", f"{len(records)} manifest(s) validated.")]

    details = ", ".join(f"{record['path'].name}: {record['error']}" for record in invalid)
    return [DiagnosticCheck("manifest_health", "fail", details)]
