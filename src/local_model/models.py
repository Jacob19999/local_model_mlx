from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RuntimePreset:
    name: str
    runtime: str
    description: str
    allow_fallback: bool = False
    model_args: dict[str, Any] = field(default_factory=dict)
    fallback_notice: str | None = None


@dataclass(slots=True)
class ModelSource:
    type: str
    location: str


@dataclass(slots=True)
class ModelManifest:
    alias: str
    display_name: str
    source: ModelSource
    local_path: str
    default_preset: str
    runtime: str
    supported_runtimes: list[str]
    turboquant_compatible: bool = False
    api_visible: bool = True
    tags: list[str] = field(default_factory=list)
    notes: str = ""

    def cache_path(self, repo_root: Path) -> Path:
        return (repo_root / self.local_path).resolve()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source"] = asdict(self.source)
        return data


@dataclass(slots=True)
class InstallAttempt:
    requested_alias: str
    source_type: str
    source_location: str
    destination_path: str
    copy_files: bool
    default_preset: str
    status: str = "pending"
    error_reason: str | None = None


@dataclass(slots=True)
class ExecutionRequest:
    model_alias: str
    prompt: str
    preset_name: str
    requested_runtime: str
    fallback_allowed: bool
    source: str
    max_tokens: int = 256
    temperature: float = 0.7


@dataclass(slots=True)
class RuntimeDecision:
    requested_runtime: str
    active_runtime: str
    fallback_used: bool
    fallback_reason: str | None = None
    notices: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GenerationResult:
    model_alias: str
    requested_runtime: str
    active_runtime: str
    output_text: str
    command: list[str] = field(default_factory=list)
    fallback_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DiagnosticCheck:
    name: str
    status: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
