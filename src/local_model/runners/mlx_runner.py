from __future__ import annotations

import shlex
import subprocess
import sys

from local_model.config import REPO_ROOT
from local_model.models import ExecutionRequest, GenerationResult, ModelManifest, RuntimeDecision
from local_model.runners.base import BaseRunner


class MLXRunner(BaseRunner):
    runtime_name = "mlx"

    def generate(
        self,
        *,
        request: ExecutionRequest,
        manifest: ModelManifest,
        decision: RuntimeDecision,
    ) -> GenerationResult:
        command = [
            sys.executable,
            "-m",
            "mlx_lm",
            "generate",
            "--model",
            str(manifest.cache_path(REPO_ROOT)),
            "--prompt",
            request.prompt,
            "--max-tokens",
            str(request.max_tokens),
            "--verbose",
            "false",
        ]
        if request.temperature is not None:
            command.extend(["--temp", str(request.temperature)])

        try:
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            output_text = completed.stdout.strip()
        except FileNotFoundError as exc:
            raise RuntimeError("Python executable not found while launching mlx_lm.") from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else ""
            raise RuntimeError(
                "Stock MLX generation failed. "
                f"Command: {shlex.join(command)}. "
                f"Details: {stderr or 'mlx_lm exited unsuccessfully.'}"
            ) from exc
        except ModuleNotFoundError as exc:
            raise RuntimeError("mlx_lm is not installed. Install MLX-LM before running models.") from exc

        return GenerationResult(
            model_alias=manifest.alias,
            requested_runtime=request.requested_runtime,
            active_runtime=decision.active_runtime,
            output_text=output_text,
            command=command,
            fallback_reason=decision.fallback_reason,
        )
