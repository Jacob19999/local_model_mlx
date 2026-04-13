from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import local_model.config as config
import local_model.doctor as doctor
import local_model.downloads as downloads
import local_model.registry as registry
import local_model.runners.mlx_runner as mlx_runner
import local_model.runners.turbo_runner as turbo_runner
import local_model.services.install_service as install_service
from local_model.downloads import cache_destination_for_alias, reset_destination
from local_model.registry import register_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENWEBUI_DOC_PATHS = {
    "readme": REPO_ROOT / "README.md",
    "agents": REPO_ROOT / "AGENTS.md",
    "quickstart": REPO_ROOT / "specs" / "003-openwebui-integration" / "quickstart.md",
    "local_model_cli_contract": REPO_ROOT / "specs" / "003-openwebui-integration" / "contracts" / "local-model-cli.md",
    "local_model_api_contract": REPO_ROOT / "specs" / "003-openwebui-integration" / "contracts" / "local-model-api.md",
    "openwebui_onboarding_contract": REPO_ROOT / "specs" / "003-openwebui-integration" / "contracts" / "openwebui-onboarding.md",
}


def assert_contains_all(text: str, snippets: list[str]) -> None:
    missing = [snippet for snippet in snippets if snippet not in text]
    assert not missing, f"Missing expected snippets: {missing}"


def assert_contains_none(text: str, snippets: list[str]) -> None:
    unexpected = [snippet for snippet in snippets if snippet in text]
    assert not unexpected, f"Unexpected snippets present: {unexpected}"


@pytest.fixture
def isolated_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    source_root = Path(config.REPO_ROOT)
    repo_root = tmp_path / "repo"
    (repo_root / "configs").mkdir(parents=True, exist_ok=True)
    (repo_root / "models" / "cache").mkdir(parents=True, exist_ok=True)
    (repo_root / "models" / "manifests").mkdir(parents=True, exist_ok=True)
    (repo_root / "forks").mkdir(parents=True, exist_ok=True)

    for relative_path in (
        "configs/models.yaml",
        "configs/presets.yaml",
        "models/manifests/template.yaml",
        "models/manifests/README.md",
    ):
        source = source_root / relative_path
        target = repo_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    cache_dir = repo_root / "models" / "cache"
    manifests_dir = repo_root / "models" / "manifests"
    config_dir = repo_root / "configs"
    forks_dir = repo_root / "forks"

    monkeypatch.setattr(config, "REPO_ROOT", repo_root)
    monkeypatch.setattr(config, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config, "CACHE_DIR", cache_dir)
    monkeypatch.setattr(config, "MANIFESTS_DIR", manifests_dir)
    monkeypatch.setattr(config, "FORKS_DIR", forks_dir)

    monkeypatch.setattr(downloads, "CACHE_DIR", cache_dir)

    monkeypatch.setattr(registry, "MANIFESTS_DIR", manifests_dir)

    monkeypatch.setattr(doctor, "CACHE_DIR", cache_dir)
    monkeypatch.setattr(doctor, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(doctor, "FORKS_DIR", forks_dir)

    monkeypatch.setattr(install_service, "REPO_ROOT", repo_root)

    monkeypatch.setattr(mlx_runner, "REPO_ROOT", repo_root)
    monkeypatch.setattr(turbo_runner, "REPO_ROOT", repo_root)

    return repo_root


@pytest.fixture(scope="session")
def openwebui_docs() -> dict[str, str]:
    return {name: path.read_text(encoding="utf-8") for name, path in OPENWEBUI_DOC_PATHS.items()}


@pytest.fixture
def valid_model_dir(tmp_path: Path) -> Path:
    model_dir = tmp_path / "valid-model"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "config.json").write_text('{"model_type": "llama"}\n', encoding="utf-8")
    (model_dir / "tokenizer.json").write_text("{}\n", encoding="utf-8")
    (model_dir / "weights.safetensors").write_text("stub\n", encoding="utf-8")
    return model_dir


@pytest.fixture
def register_test_manifest(isolated_repo, valid_model_dir):
    def _register(alias: str = "demo-openwebui"):
        destination = cache_destination_for_alias(alias)
        reset_destination(destination)
        shutil.copytree(valid_model_dir, destination, dirs_exist_ok=True)
        return register_manifest(
            alias=alias,
            source_type="local_dir",
            source_location=str(valid_model_dir),
            local_path=f"models/cache/{alias}",
        )

    return _register


@pytest.fixture
def parse_sse_events():
    def _parse(lines: list[str]) -> list[object]:
        events: list[object] = []
        for line in lines:
            if not line.startswith("data: "):
                continue
            payload = line.removeprefix("data: ")
            if payload == "[DONE]":
                events.append(payload)
                continue
            events.append(json.loads(payload))
        return events

    return _parse
