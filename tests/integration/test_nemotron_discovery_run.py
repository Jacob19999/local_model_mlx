from __future__ import annotations

import json

from local_model.cli import generate_once, main
from local_model.models import GenerationResult, RuntimeCapabilityProfile


def test_nemotron_is_discoverable_with_capabilities_and_runs_on_stock_mlx(
    register_test_manifest,
    monkeypatch,
    capsys,
) -> None:
    register_test_manifest("nemotron-3-nano-30b-a3b")
    monkeypatch.setattr("local_model.services.runtime_resolver._mlx_available", lambda: True)

    def fake_generate(self, *, request, manifest, decision):
        return GenerationResult(
            model_alias=manifest.alias,
            requested_runtime=request.requested_runtime,
            active_runtime=decision.active_runtime,
            output_text="Nemotron loaded successfully.",
            finish_reason="stop",
            fallback_reason=decision.fallback_reason,
            capabilities=decision.capabilities,
        )

    monkeypatch.setattr("local_model.runners.mlx_runner.MLXRunner.generate", fake_generate)

    assert main(["list-models", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["models"][0]["alias"] == "nemotron-3-nano-30b-a3b"
    assert payload["models"][0]["capabilities"] == {
        "supports_streaming": True,
        "reasoning_format": "think_tags",
        "reasoning_enabled_by_default": True,
    }

    result = generate_once(
        model_alias="nemotron-3-nano-30b-a3b",
        prompt="Say hello",
        preset_name="mlx-api-reasoning",
        requested_runtime="mlx",
        fallback_allowed=False,
        source="integration-test",
        max_tokens=32,
        temperature=0.2,
    )
    assert result.active_runtime == "mlx"
    assert result.output_text == "Nemotron loaded successfully."
    assert result.capabilities == RuntimeCapabilityProfile(
        supports_streaming=True,
        reasoning_format="think_tags",
        reasoning_enabled_by_default=True,
    )
