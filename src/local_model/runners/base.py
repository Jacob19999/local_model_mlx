from __future__ import annotations

from abc import ABC, abstractmethod

from local_model.models import ExecutionRequest, GenerationResult, ModelManifest, RuntimeDecision


class BaseRunner(ABC):
    runtime_name: str

    @abstractmethod
    def generate(
        self,
        *,
        request: ExecutionRequest,
        manifest: ModelManifest,
        decision: RuntimeDecision,
    ) -> GenerationResult:
        raise NotImplementedError

