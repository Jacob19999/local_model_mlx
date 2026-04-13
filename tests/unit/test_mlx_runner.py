from __future__ import annotations

from types import SimpleNamespace

from local_model.models import (
    ExecutionRequest,
    ModelManifest,
    ModelSource,
    RuntimeCapabilityProfile,
    RuntimeDecision,
)
from local_model.runners.mlx_runner import MLXRunner


def _manifest() -> ModelManifest:
    return ModelManifest(
        alias="nemotron-3-nano-30b-a3b",
        display_name="Install Nemotron 3 Nano 30B A3B",
        source=ModelSource(
            type="hf_repo",
            location="lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit",
        ),
        local_path="models/cache/nemotron-3-nano-30b-a3b",
        default_preset="mlx-api-reasoning",
        runtime="mlx",
        supported_runtimes=["mlx"],
        turboquant_compatible=False,
        capabilities=RuntimeCapabilityProfile(
            supports_streaming=True,
            reasoning_format="think_tags",
            reasoning_enabled_by_default=True,
        ),
    )


def _request() -> ExecutionRequest:
    return ExecutionRequest(
        model_alias="nemotron-3-nano-30b-a3b",
        prompt="Reply with OK.",
        preset_name="mlx-api-reasoning",
        requested_runtime="mlx",
        fallback_allowed=False,
        source="test",
        max_tokens=16,
        temperature=0.0,
        stream=True,
    )


def _decision() -> RuntimeDecision:
    return RuntimeDecision(
        requested_runtime="mlx",
        active_runtime="mlx",
        fallback_used=False,
        streaming_requested=True,
        capabilities=RuntimeCapabilityProfile(
            supports_streaming=True,
            reasoning_format="think_tags",
            reasoning_enabled_by_default=True,
        ),
    )


def test_mlx_runner_streams_incremental_deltas_and_strips_reasoning(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeMLX:
        @staticmethod
        def load(model_path):
            captured["model_path"] = model_path
            return object(), object()

        @staticmethod
        def stream_generate(model, tokenizer, prompt, **kwargs):
            captured["prompt"] = prompt
            captured["kwargs"] = kwargs
            yield SimpleNamespace(text="<think>step ", finish_reason=None)
            yield SimpleNamespace(text="one</think>Answer", finish_reason="stop")

    monkeypatch.setattr("local_model.runners.mlx_runner.mlx_lm", FakeMLX)

    deltas = list(MLXRunner().stream(request=_request(), manifest=_manifest(), decision=_decision()))

    assert captured["prompt"] == "Reply with OK."
    assert captured["kwargs"] == {"max_tokens": 16, "temp": 0.0}
    assert deltas[0].reasoning_delta == "step "
    assert deltas[1].reasoning_delta == "one"
    assert deltas[1].content_delta == "Answer"
    assert deltas[1].finish_reason == "stop"


def test_mlx_runner_generate_accumulates_answer_and_reasoning(monkeypatch) -> None:
    class FakeMLX:
        @staticmethod
        def load(model_path):
            return object(), object()

        @staticmethod
        def stream_generate(model, tokenizer, prompt, **kwargs):
            yield SimpleNamespace(text="Hello ", finish_reason=None)
            yield SimpleNamespace(text="<think>scratch</think>world", finish_reason="stop")

    monkeypatch.setattr("local_model.runners.mlx_runner.mlx_lm", FakeMLX)

    result = MLXRunner().generate(request=_request(), manifest=_manifest(), decision=_decision())

    assert result.output_text == "Hello world"
    assert result.reasoning_text == "scratch"
    assert result.finish_reason == "stop"
    assert result.capabilities.supports_streaming is True
    assert result.command[:3] == [result.command[0], "-m", "mlx_lm.stream_generate"]
