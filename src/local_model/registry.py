from __future__ import annotations

import re
from pathlib import Path

from local_model.config import MANIFESTS_DIR, load_models_config, read_data_file, write_data_file
from local_model.models import ModelManifest, ModelSource


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def manifest_path_for_alias(alias: str) -> Path:
    return MANIFESTS_DIR / f"{slugify(alias)}.yaml"


def parse_manifest(payload: dict) -> ModelManifest:
    source = payload.get("source", {})
    supported_runtimes = payload.get("supported_runtimes") or [payload.get("runtime", "mlx")]
    return ModelManifest(
        alias=payload["alias"],
        display_name=payload.get("display_name", payload["alias"]),
        source=ModelSource(type=source["type"], location=source["location"]),
        local_path=payload["local_path"],
        default_preset=payload.get("default_preset", "mlx-chat"),
        runtime=payload.get("runtime", "mlx"),
        supported_runtimes=supported_runtimes,
        turboquant_compatible=payload.get("turboquant_compatible", False),
        api_visible=payload.get("api_visible", True),
        tags=payload.get("tags", []),
        notes=payload.get("notes", ""),
    )


def list_manifests() -> list[ModelManifest]:
    manifests: list[ModelManifest] = []
    for path in sorted(MANIFESTS_DIR.glob("*.yaml")):
        if path.name == "template.yaml":
            continue
        payload = read_data_file(path)
        manifests.append(parse_manifest(payload))
    return manifests


def get_manifest(alias: str) -> ModelManifest:
    normalized = slugify(alias)
    for manifest in list_manifests():
        if slugify(manifest.alias) == normalized:
            return manifest
    raise KeyError(f"Unknown model alias: {alias}")


def register_manifest(
    *,
    alias: str,
    source_type: str,
    source_location: str,
    local_path: str,
    display_name: str | None = None,
    default_preset: str | None = None,
    turboquant_compatible: bool = False,
    api_visible: bool = True,
    tags: list[str] | None = None,
    notes: str = "",
) -> ModelManifest:
    defaults = load_models_config().get("manifest_defaults", {})
    payload = {
        "alias": alias,
        "display_name": display_name or alias,
        "source": {
            "type": source_type,
            "location": source_location,
        },
        "local_path": local_path,
        "default_preset": default_preset or defaults.get("default_preset", "mlx-chat"),
        "runtime": defaults.get("runtime", "mlx"),
        "supported_runtimes": sorted(
            set(defaults.get("supported_runtimes", ["mlx"])) | ({"turboquant"} if turboquant_compatible else set())
        ),
        "turboquant_compatible": turboquant_compatible,
        "api_visible": api_visible,
        "tags": tags or [],
        "notes": notes,
    }
    path = manifest_path_for_alias(alias)
    write_data_file(path, payload)
    return parse_manifest(payload)

