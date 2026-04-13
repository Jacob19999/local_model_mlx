from __future__ import annotations

from local_model.cli import DEFAULT_OPENWEBUI_API_URL, DOCKER_OPENWEBUI_API_URL, main


def test_cli_ui_prints_openwebui_migration_guidance_and_exits_non_zero(capsys) -> None:
    assert main(["ui"]) == 1

    output = capsys.readouterr().out
    assert "`local-model ui` has been retired" in output
    assert "local-model serve --host 127.0.0.1 --port 8000" in output
    assert DEFAULT_OPENWEBUI_API_URL in output
    assert DOCKER_OPENWEBUI_API_URL in output


def test_cli_ui_includes_service_down_and_no_models_recovery_checks(capsys) -> None:
    assert main(["ui"]) == 1

    output = capsys.readouterr().out
    assert "curl http://127.0.0.1:8000/health" in output
    assert "curl http://127.0.0.1:8000/v1/models" in output
    assert "local-model list-models --json" in output


def test_cli_ui_normalizes_custom_api_base_url_for_wrong_endpoint_guidance(capsys) -> None:
    assert main(["ui", "--api-base-url", "http://localhost:9001/"]) == 1

    output = capsys.readouterr().out
    assert "http://localhost:9001/v1" in output
    assert "curl http://localhost:9001/health" in output
    assert "correct the Open WebUI connection URL to http://localhost:9001/v1" in output
