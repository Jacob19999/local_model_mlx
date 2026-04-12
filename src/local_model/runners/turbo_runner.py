from __future__ import annotations

import os
import shlex
import subprocess

from local_model.config import REPO_ROOT
from local_model.models import ExecutionRequest, GenerationResult, ModelManifest, RuntimeDecision
from local_model.runners.base import BaseRunner


class TurboRunner(BaseRunner):
    runtime_name = "turboquant"

    @staticmethod
    def turbo_command() -> list[str] | None:
        raw = os.environ.get("LOCAL_MODEL_TURBO_COMMAND")
        if raw:
            return shlex.split(raw)
        return None

    def generate(
        self,
        *,
        request: ExecutionRequest,
        manifest: ModelManifest,
        decision: RuntimeDecision,
    ) -> GenerationResult:
        command = self.turbo_command()
        if not command:
            raise RuntimeError(
                "TurboQuant integration is not configured. Set LOCAL_MODEL_TURBO_COMMAND or install mlx_turboquant."
            )

        full_command = command + [
            "--model",
            str(manifest.cache_path(REPO_ROOT)),
            "--prompt",
            request.prompt,
            "--max-tokens",
            str(request.max_tokens),
        ]

        try:
            completed = subprocess.run(
                full_command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else ""
            raise RuntimeError(
                "TurboQuant generation failed. "
                f"Command: {shlex.join(full_command)}. "
                f"Details: {stderr or 'command exited unsuccessfully.'}"
            ) from exc

        return GenerationResult(
            model_alias=manifest.alias,
            requested_runtime=request.requested_runtime,
            active_runtime=decision.active_runtime,
            output_text=completed.stdout.strip(),
            command=full_command,
            fallback_reason=decision.fallback_reason,
        )
