from __future__ import annotations

import shutil

import pytest

from local_model.downloads import cache_destination_for_alias, reset_destination
from local_model.registry import AliasConflictError, manifest_path_for_alias, register_manifest
from local_model.services.install_service import InstallService


def test_successful_nemotron_install_writes_manifest(isolated_repo, valid_model_dir, monkeypatch) -> None:
    def fake_install(alias: str, source: str):
        destination = cache_destination_for_alias(alias)
        reset_destination(destination)
        shutil.copytree(valid_model_dir, destination, dirs_exist_ok=True)
        return destination

    monkeypatch.setattr("local_model.services.install_service.install_from_hf_repo", fake_install)

    manifest = InstallService().install(
        alias="nemotron-3-nano-30b-a3b",
        source_type="hf_repo",
        source="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
    )

    assert manifest.alias == "nemotron-3-nano-30b-a3b"
    assert manifest.display_name == "Install Nemotron 3 Nano 30B A3B"
    assert manifest.tags == ["text-generation", "nemotron", "mlx"]
    assert manifest_path_for_alias(manifest.alias).exists()
    assert cache_destination_for_alias(manifest.alias).exists()


def test_alias_conflict_preserves_existing_registration(isolated_repo, valid_model_dir, monkeypatch) -> None:
    original = register_manifest(
        alias="nemotron-3-nano-30b-a3b",
        source_type="hf_repo",
        source_location="someone-else/nemotron",
        local_path="models/cache/original",
    )
    original_path = manifest_path_for_alias(original.alias)
    original_contents = original_path.read_text(encoding="utf-8")

    def fake_install(alias: str, source: str):
        raise AssertionError("download should not run when alias conflict exists")

    monkeypatch.setattr("local_model.services.install_service.install_from_hf_repo", fake_install)

    with pytest.raises(AliasConflictError):
        InstallService().install(
            alias="nemotron-3-nano-30b-a3b",
            source_type="hf_repo",
            source="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        )

    assert original_path.read_text(encoding="utf-8") == original_contents
