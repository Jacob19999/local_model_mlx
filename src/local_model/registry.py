from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from local_model.config import MANIFESTS_DIR, load_models_config, read_data_file
from local_model.models import ModelManifest, ModelSource


class AliasConflictError(RuntimeError):
    pass


class ManifestValidationError(RuntimeError):
    pass


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def manifest_path_for_alias(alias: str) -> Path:
    return MANIFESTS_DIR / f"{slugify(alias)}.yaml"


def supported_source_types() -> set[str]:
    config = load_models_config()
    return set(config.get("supported_sources", {}).keys())


def get_model_profile(alias: str) -> dict[str, Any] | None:
    profiles = load_models_config().get("supported_models", [])
    normalized = slugify(alias)
    for item in profiles:
        aliases = [item.get("alias", ""), *item.get("aliases", [])]
        if any(slugify(candidate) == normalized for candidate in aliases if candidate):
            return item
    return None


def resolve_install_source(
    alias: str,
    source_type: str | None,
    source_location: str | None,
) -> ModelSource:
    if source_type and source_location:
        return ModelSource(type=source_type, location=source_location)

    profile = get_model_profile(alias) or {}
    canonical = profile.get("canonical_source", {})
    resolved_type = source_type or canonical.get("type")
    resolved_location = source_location or canonical.get("location")
    if not resolved_type or not resolved_location:
        raise ManifestValidationError(
            "A source type and source location are required for this alias."
        )
    return ModelSource(type=resolved_type, location=resolved_location)


def validate_manifest_payload(payload: dict[str, Any]) -> None:
    alias = str(payload.get("alias", "")).strip()
    if not alias:
        raise ManifestValidationError("Manifest alias is required.")

    source = payload.get("source", {})
    source_type = str(source.get("type", "")).strip()
    source_location = str(source.get("location", "")).strip()
    if not source_type or not source_location:
        raise ManifestValidationError(f"Manifest `{alias}` must define source.type and source.location.")
    if source_type not in supported_source_types():
        raise ManifestValidationError(f"Manifest `{alias}` uses unsupported source type `{source_type}`.")

    local_path = str(payload.get("local_path", "")).strip()
    if not local_path:
        raise ManifestValidationError(f"Manifest `{alias}` must define local_path.")

    runtime = str(payload.get("runtime", "")).strip()
    supported_runtimes = payload.get("supported_runtimes") or []
    if not runtime:
        raise ManifestValidationError(f"Manifest `{alias}` must define a default runtime.")
    if runtime not in supported_runtimes:
        raise ManifestValidationError(
            f"Manifest `{alias}` declares runtime `{runtime}` but does not include it in supported_runtimes."
        )
    if payload.get("turboquant_compatible") and "turboquant" not in supported_runtimes:
        raise ManifestValidationError(
            f"Manifest `{alias}` cannot declare turboquant_compatible without a turboquant runtime."
        )


def _normalize_manifest_payload(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("source", {})
    defaults = load_models_config().get("manifest_defaults", {})
    supported_runtimes = payload.get("supported_runtimes") or [payload.get("runtime", defaults.get("runtime", "mlx"))]
    normalized = {
        "alias": payload.get("alias", ""),
        "display_name": payload.get("display_name", payload.get("alias", "")),
        "source": {
            "type": source.get("type", ""),
            "location": source.get("location", ""),
        },
        "local_path": payload.get("local_path", ""),
        "default_preset": payload.get("default_preset", defaults.get("default_preset", "mlx-chat")),
        "runtime": payload.get("runtime", defaults.get("runtime", "mlx")),
        "supported_runtimes": sorted(set(supported_runtimes)),
        "turboquant_compatible": bool(payload.get("turboquant_compatible", False)),
        "api_visible": bool(payload.get("api_visible", defaults.get("api_visible", True))),
        "tags": payload.get("tags", []),
        "notes": payload.get("notes", ""),
    }
    validate_manifest_payload(normalized)
    return normalized


def build_manifest_payload(
    *,
    alias: str,
    source_type: str,
    source_location: str,
    local_path: str,
    display_name: str | None = None,
    default_preset: str | None = None,
    turboquant_compatible: bool = False,
    api_visible: bool | None = None,
    tags: list[str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    defaults = load_models_config().get("manifest_defaults", {})
    profile = get_model_profile(alias) or {}
    runtime = profile.get("runtime", defaults.get("runtime", "mlx"))
    supported_runtimes = list(profile.get("supported_runtimes", defaults.get("supported_runtimes", [runtime])))
    effective_turbo = bool(profile.get("turboquant_compatible", defaults.get("turboquant_compatible", False)))
    effective_turbo = turboquant_compatible or effective_turbo
    if effective_turbo and "turboquant" not in supported_runtimes:
        supported_runtimes.append("turboquant")

    payload = {
        "alias": alias,
        "display_name": display_name or profile.get("display_name", alias),
        "source": {
            "type": source_type,
            "location": source_location,
        },
        "local_path": local_path,
        "default_preset": default_preset or profile.get("default_preset", defaults.get("default_preset", "mlx-chat")),
        "runtime": runtime,
        "supported_runtimes": sorted(set(supported_runtimes)),
        "turboquant_compatible": effective_turbo,
        "api_visible": profile.get("api_visible", defaults.get("api_visible", True)) if api_visible is None else api_visible,
        "tags": list(tags if tags is not None else profile.get("tags", [])),
        "notes": notes or profile.get("notes", ""),
    }
    validate_manifest_payload(payload)
    return payload


def parse_manifest(payload: dict[str, Any]) -> ModelManifest:
    normalized = _normalize_manifest_payload(payload)
    source = normalized["source"]
    return ModelManifest(
        alias=normalized["alias"],
        display_name=normalized["display_name"],
        source=ModelSource(type=source["type"], location=source["location"]),
        local_path=normalized["local_path"],
        default_preset=normalized["default_preset"],
        runtime=normalized["runtime"],
        supported_runtimes=normalized["supported_runtimes"],
        turboquant_compatible=normalized["turboquant_compatible"],
        api_visible=normalized["api_visible"],
        tags=normalized["tags"],
        notes=normalized["notes"],
    )


def inspect_manifests() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(MANIFESTS_DIR.glob("*.yaml")):
        if path.name == "template.yaml":
            continue
        try:
            payload = read_data_file(path)
            manifest = parse_manifest(payload)
            records.append({"path": path, "manifest": manifest, "error": None})
        except Exception as exc:
            records.append({"path": path, "manifest": None, "error": str(exc)})
    return records


def list_manifests() -> list[ModelManifest]:
    manifests: list[ModelManifest] = []
    for record in inspect_manifests():
        if record["manifest"] is not None:
            manifests.append(record["manifest"])
    return manifests


def get_manifest(alias: str) -> ModelManifest:
    normalized = slugify(alias)
    for manifest in list_manifests():
        if slugify(manifest.alias) == normalized:
            return manifest
    raise KeyError(f"Unknown model alias: {alias}")


def ensure_alias_available(alias: str, source_type: str, source_location: str) -> None:
    normalized = slugify(alias)
    for manifest in list_manifests():
        if slugify(manifest.alias) != normalized:
            continue
        if manifest.source.type == source_type and manifest.source.location == source_location:
            return
        raise AliasConflictError(
            f"Alias `{alias}` already maps to `{manifest.source.type}:{manifest.source.location}`. "
            "Choose a different alias or remove the existing manifest first."
        )


def _write_manifest_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    temp_path.replace(path)


def register_manifest(
    *,
    alias: str,
    source_type: str | None,
    source_location: str | None,
    local_path: str,
    display_name: str | None = None,
    default_preset: str | None = None,
    turboquant_compatible: bool = False,
    api_visible: bool = True,
    tags: list[str] | None = None,
    notes: str = "",
) -> ModelManifest:
    source = resolve_install_source(alias, source_type, source_location)
    ensure_alias_available(alias, source.type, source.location)
    payload = build_manifest_payload(
        alias=alias,
        source_type=source.type,
        source_location=source.location,
        local_path=local_path,
        display_name=display_name,
        default_preset=default_preset,
        turboquant_compatible=turboquant_compatible,
        api_visible=api_visible,
        tags=tags,
        notes=notes,
    )
    path = manifest_path_for_alias(alias)
    _write_manifest_payload(path, payload)
    return parse_manifest(payload)
