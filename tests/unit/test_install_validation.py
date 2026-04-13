from __future__ import annotations

import shutil

import pytest

from local_model.downloads import DownloadError, cache_destination_for_alias, reset_destination, validate_artifact_set
from local_model.registry import AliasConflictError, register_manifest
from local_model.services.install_service import InstallService


def test_validate_artifact_set_rejects_incomplete_model(tmp_path) -> None:
    invalid_dir = tmp_path / "invalid-model"
    invalid_dir.mkdir()
    (invalid_dir / "tokenizer.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(DownloadError, match="config.json"):
        validate_artifact_set(invalid_dir, "hf_repo")


def test_install_rejects_alias_conflicts_before_download(isolated_repo, valid_model_dir, monkeypatch) -> None:
    register_manifest(
        alias="nemotron-3-nano-30b-a3b",
        source_type="hf_repo",
        source_location="someone-else/nemotron",
        local_path="models/cache/existing",
    )

    def fail_if_called(alias: str, source: str):
        raise AssertionError("download should not start when alias is already taken")

    monkeypatch.setattr("local_model.services.install_service.install_from_hf_repo", fail_if_called)

    with pytest.raises(AliasConflictError):
        InstallService().install(
            alias="nemotron-3-nano-30b-a3b",
            source_type="hf_repo",
            source="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        )


def test_install_cleans_partial_downloads_after_validation_failure(isolated_repo, valid_model_dir, monkeypatch) -> None:
    def fake_install(alias: str, source: str):
        destination = cache_destination_for_alias(alias)
        reset_destination(destination)
        shutil.copytree(valid_model_dir, destination, dirs_exist_ok=True)
        (destination / "tokenizer.json").unlink()
        return destination

    monkeypatch.setattr("local_model.services.install_service.install_from_hf_repo", fake_install)

    with pytest.raises(DownloadError, match="tokenizer metadata"):
        InstallService().install(
            alias="nemotron-3-nano-30b-a3b",
            source_type="hf_repo",
            source="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        )

    assert not cache_destination_for_alias("nemotron-3-nano-30b-a3b").exists()
