from __future__ import annotations

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


@pytest.fixture
def valid_model_dir(tmp_path: Path) -> Path:
    model_dir = tmp_path / "valid-model"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "config.json").write_text('{"model_type": "llama"}\n', encoding="utf-8")
    (model_dir / "tokenizer.json").write_text("{}\n", encoding="utf-8")
    (model_dir / "weights.safetensors").write_text("stub\n", encoding="utf-8")
    return model_dir
