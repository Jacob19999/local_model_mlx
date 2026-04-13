from __future__ import annotations

import shutil

from local_model.cli import main
from local_model.downloads import cache_destination_for_alias, reset_destination
from local_model.registry import register_manifest


def test_cli_install_reports_interrupted_artifacts(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "local_model.services.install_service.InstallService.install",
        lambda self, **_: (_ for _ in ()).throw(RuntimeError("Installed artifacts are incomplete: missing tokenizer metadata")),
    )

    assert (
        main(
            [
                "install",
                "nemotron-3-nano-30b-a3b",
                "--source-type",
                "hf_repo",
                "--source",
                "lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
            ]
        )
        == 1
    )
    assert "error: Installed artifacts are incomplete" in capsys.readouterr().err


def test_cli_run_blocks_unsupported_runtime_without_fallback(isolated_repo, valid_model_dir, capsys) -> None:
    destination = cache_destination_for_alias("nemotron-3-nano-30b-a3b")
    reset_destination(destination)
    shutil.copytree(valid_model_dir, destination, dirs_exist_ok=True)
    register_manifest(
        alias="nemotron-3-nano-30b-a3b",
        source_type="hf_repo",
        source_location="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        local_path="models/cache/nemotron-3-nano-30b-a3b",
    )

    assert (
        main(
            [
                "run",
                "nemotron-3-nano-30b-a3b",
                "--runtime",
                "turboquant",
                "--no-fallback",
                "--prompt",
                "This should fail",
            ]
        )
        == 1
    )
    assert "error: Manifest runtime list excludes `turboquant`." in capsys.readouterr().err
