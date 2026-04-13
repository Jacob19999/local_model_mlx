from __future__ import annotations

import json

from local_model.cli import main
from local_model.models import ModelManifest, ModelSource


def test_cli_install_returns_manifest_json(monkeypatch, capsys) -> None:
    manifest = ModelManifest(
        alias="nemotron-3-nano-30b-a3b",
        display_name="Install Nemotron 3 Nano 30B A3B",
        source=ModelSource(
            type="hf_repo",
            location="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        ),
        local_path="models/cache/nemotron-3-nano-30b-a3b",
        default_preset="mlx-chat",
        runtime="mlx",
        supported_runtimes=["mlx"],
        turboquant_compatible=False,
        api_visible=True,
        tags=["text-generation", "nemotron", "mlx"],
    )

    monkeypatch.setattr("local_model.services.install_service.InstallService.install", lambda self, **_: manifest)

    assert main(
        [
            "install",
            "nemotron-3-nano-30b-a3b",
            "--source-type",
            "hf_repo",
            "--source",
            "lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
            "--json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["alias"] == "nemotron-3-nano-30b-a3b"
    assert payload["source_type"] == "hf_repo"
    assert payload["runtime"] == "mlx"
    assert payload["supported_runtimes"] == ["mlx"]


def test_cli_install_surfaces_stderr_failures(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "local_model.services.install_service.InstallService.install",
        lambda self, **_: (_ for _ in ()).throw(RuntimeError("incomplete or invalid downloaded artifact set")),
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
    assert "error: incomplete or invalid downloaded artifact set" in capsys.readouterr().err
