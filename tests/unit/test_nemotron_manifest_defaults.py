from __future__ import annotations

from local_model.registry import build_manifest_payload, get_model_profile, resolve_install_source


def test_nemotron_profile_exposes_canonical_source(isolated_repo) -> None:
    profile = get_model_profile("nemotron-3-nano-30b-a3b")
    assert profile is not None
    assert profile["canonical_source"]["type"] == "hf_repo"
    assert profile["canonical_source"]["location"] == (
        "lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit"
    )

    source = resolve_install_source("nemotron-3-nano-30b-a3b", None, None)
    assert source.type == "hf_repo"
    assert source.location == profile["canonical_source"]["location"]


def test_nemotron_manifest_defaults_are_applied(isolated_repo) -> None:
    payload = build_manifest_payload(
        alias="nemotron-3-nano-30b-a3b",
        source_type="hf_repo",
        source_location="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        local_path="models/cache/nemotron-3-nano-30b-a3b",
    )

    assert payload["display_name"] == "Install Nemotron 3 Nano 30B A3B"
    assert payload["default_preset"] == "mlx-chat"
    assert payload["runtime"] == "mlx"
    assert payload["supported_runtimes"] == ["mlx"]
    assert payload["turboquant_compatible"] is False
    assert payload["api_visible"] is True
    assert payload["tags"] == ["text-generation", "nemotron", "mlx"]
    assert "stock MLX runs" in payload["notes"]
