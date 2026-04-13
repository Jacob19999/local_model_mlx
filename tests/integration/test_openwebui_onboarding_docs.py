from __future__ import annotations

from conftest import assert_contains_all, assert_contains_none


def test_supported_surface_docs_point_to_openwebui(openwebui_docs) -> None:
    assert_contains_all(
        openwebui_docs["readme"],
        [
            "Open WebUI",
            "http://127.0.0.1:8000/v1",
            "local-model serve",
            "local-model ui",
        ],
    )
    assert_contains_all(
        openwebui_docs["agents"],
        [
            "Open WebUI",
            "Python 3.11 runtime",
        ],
    )
    assert_contains_all(
        openwebui_docs["openwebui_onboarding_contract"],
        [
            "Open WebUI",
            "http://127.0.0.1:8000/v1",
            "/v1/models",
        ],
    )


def test_supported_surface_docs_remove_native_ui_launch_guidance(openwebui_docs) -> None:
    for key in ("readme", "agents", "local_model_cli_contract", "openwebui_onboarding_contract"):
        assert_contains_none(
            openwebui_docs[key],
            [
                "Launch the SwiftUI shell",
                "Swift / Xcode if you want to launch the macOS UI",
                "apps/macos-ui/",
            ],
        )


def test_openwebui_docs_include_troubleshooting_and_verification_commands(openwebui_docs) -> None:
    assert_contains_all(
        openwebui_docs["readme"],
        [
            "curl http://127.0.0.1:8000/health",
            "curl http://127.0.0.1:8000/v1/models",
            "local-model list-models --json",
        ],
    )
    assert_contains_all(
        openwebui_docs["quickstart"],
        [
            "curl http://127.0.0.1:8000/health",
            "curl http://127.0.0.1:8000/v1/models",
            "If Open WebUI is running in Docker instead of natively",
        ],
    )
    assert_contains_all(
        openwebui_docs["local_model_api_contract"],
        [
            "curl http://127.0.0.1:8000/health",
            "curl http://127.0.0.1:8000/v1/models",
        ],
    )
