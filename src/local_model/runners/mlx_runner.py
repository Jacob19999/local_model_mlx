from __future__ import annotations

import sys
from typing import Iterator

from local_model.config import REPO_ROOT
from local_model.models import ExecutionRequest, GenerationDelta, GenerationResult, ModelManifest, RuntimeDecision
from local_model.runners.base import BaseRunner
from local_model.services.reasoning_parser import ReasoningParser

try:
    import mlx_lm
except ImportError:  # pragma: no cover - exercised via runtime checks
    mlx_lm = None


class MLXRunner(BaseRunner):
    runtime_name = "mlx"

    @staticmethod
    def _build_command(manifest: ModelManifest, request: ExecutionRequest) -> list[str]:
        command = [
            sys.executable,
            "-m",
            "mlx_lm.stream_generate",
            "--model",
            str(manifest.cache_path(REPO_ROOT)),
            "--prompt",
            request.prompt,
            "--max-tokens",
            str(request.max_tokens),
        ]
        if request.temperature is not None:
            command.extend(["--temp", str(request.temperature)])
        return command

    @staticmethod
    def _load_runtime() -> object:
        if mlx_lm is None:
            raise RuntimeError("mlx_lm is not installed. Install MLX-LM before running models.")
        return mlx_lm

    def stream(
        self,
        *,
        request: ExecutionRequest,
        manifest: ModelManifest,
        decision: RuntimeDecision,
    ) -> Iterator[GenerationDelta]:
        backend = self._load_runtime()
        model_path = str(manifest.cache_path(REPO_ROOT))
        try:
            model, tokenizer = backend.load(model_path)
        except FileNotFoundError as exc:
            raise RuntimeError(f"Model files were not found at `{model_path}`.") from exc
        except Exception as exc:  # pragma: no cover - depends on local mlx runtime state
            raise RuntimeError(f"Stock MLX model load failed for `{model_path}`: {exc}") from exc

        parser = ReasoningParser(decision.capabilities.reasoning_format)
        kwargs = {"max_tokens": request.max_tokens}
        if request.temperature is not None:
            kwargs["temp"] = request.temperature

        def iterator() -> Iterator[GenerationDelta]:
            sequence = 0
            try:
                for response in backend.stream_generate(model, tokenizer, request.prompt, **kwargs):
                    content_delta, reasoning_delta = parser.feed(response.text or "")
                    if response.finish_reason is not None:
                        final_content, final_reasoning = parser.finalize()
                        content_delta += final_content
                        reasoning_delta += final_reasoning

                    if not content_delta and not reasoning_delta and response.finish_reason is None:
                        continue

                    sequence += 1
                    yield GenerationDelta(
                        sequence=sequence,
                        content_delta=content_delta,
                        reasoning_delta=reasoning_delta,
                        finish_reason=response.finish_reason,
                    )
            except Exception as exc:  # pragma: no cover - depends on local mlx runtime state
                raise RuntimeError(f"Stock MLX generation failed for `{manifest.alias}`: {exc}") from exc

        return iterator()

    def generate(
        self,
        *,
        request: ExecutionRequest,
        manifest: ModelManifest,
        decision: RuntimeDecision,
    ) -> GenerationResult:
        deltas = list(self.stream(request=request, manifest=manifest, decision=decision))
        output_text = "".join(delta.content_delta for delta in deltas)
        reasoning_text = "".join(delta.reasoning_delta for delta in deltas)
        finish_reason = next((delta.finish_reason for delta in reversed(deltas) if delta.finish_reason), "stop")
        parser = ReasoningParser(decision.capabilities.reasoning_format)
        if output_text:
            parser.transcript.answer_buffer = output_text
        if reasoning_text:
            parser.transcript.raw_buffer = reasoning_text
            parser.transcript.normalized_buffer = reasoning_text
        return GenerationResult(
            model_alias=manifest.alias,
            requested_runtime=request.requested_runtime,
            active_runtime=decision.active_runtime,
            output_text=output_text,
            reasoning_text=reasoning_text,
            finish_reason=finish_reason,
            transcript=parser.transcript,
            command=self._build_command(manifest, request),
            fallback_reason=decision.fallback_reason,
            capabilities=decision.capabilities,
            notices=decision.notices,
        )
