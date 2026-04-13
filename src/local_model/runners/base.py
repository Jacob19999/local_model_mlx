from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from local_model.models import ExecutionRequest, GenerationDelta, GenerationResult, ModelManifest, RuntimeDecision


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

    @abstractmethod
    def stream(
        self,
        *,
        request: ExecutionRequest,
        manifest: ModelManifest,
        decision: RuntimeDecision,
    ) -> Iterator[GenerationDelta]:
        raise NotImplementedError
