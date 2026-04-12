from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from local_model.models import RuntimePreset


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "configs"
MANIFESTS_DIR = REPO_ROOT / "models" / "manifests"
CACHE_DIR = REPO_ROOT / "models" / "cache"
FORKS_DIR = REPO_ROOT / "forks"


def read_data_file(path: Path) -> Any:
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return {}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"{path} is not JSON-compatible YAML and PyYAML is not installed."
            ) from exc
        return yaml.safe_load(content)


def write_data_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def load_models_config() -> dict[str, Any]:
    return read_data_file(CONFIG_DIR / "models.yaml")


def load_presets() -> dict[str, RuntimePreset]:
    raw = read_data_file(CONFIG_DIR / "presets.yaml")
    presets: dict[str, RuntimePreset] = {}
    for item in raw.get("presets", []):
        preset = RuntimePreset(
            name=item["name"],
            runtime=item["runtime"],
            description=item["description"],
            allow_fallback=item.get("allow_fallback", False),
            model_args=item.get("model_args", {}),
            fallback_notice=item.get("fallback_notice"),
        )
        presets[preset.name] = preset
    return presets

