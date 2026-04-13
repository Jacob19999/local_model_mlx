# Research: Add streaming chat completions with reasoning output

## Decision 1: Move stock MLX chat generation onto the native `mlx_lm` streaming API

- **Decision**: Use the installed `mlx_lm` Python library directly for stock MLX generation so the runner can expose both one-shot and incremental token emission from a shared runtime path.
- **Rationale**: The current `MLXRunner` shells out to `python -m mlx_lm generate`, which only returns buffered stdout after generation completes. That path cannot satisfy the feature requirement for true runner-layer incremental output. Local inspection of the installed library shows that `mlx_lm.stream_generate(...)` yields per-segment text plus a terminal `finish_reason`, which is a better fit for the new API contract than parsing buffered subprocess stdout.
- **Alternatives considered**:
  - Continue using the subprocess CLI and split stdout into fake chunks: rejected because it violates the spec requirement for real incremental generation.
  - Stream subprocess stdout directly: rejected because the CLI surface in use today is not a stable token-stream contract and would still couple the feature to text buffering behavior outside the repository.

## Decision 2: Use Server-Sent Events with OpenAI-style chat-completion chunks

- **Decision**: Implement streamed chat responses as `text/event-stream` output that emits JSON `chat.completion.chunk` payloads and ends successful streams with the standard `data: [DONE]` sentinel.
- **Rationale**: This keeps the existing `POST /v1/chat/completions` route while aligning the streamed transport with the client expectations behind OpenAI-compatible consumers. It also gives the feature a clear completion signal without changing the non-streaming response shape for existing clients.
- **Alternatives considered**:
  - Add a second streaming endpoint: rejected because the existing OpenAI-compatible surface should remain the single public API path.
  - Return newline-delimited JSON without SSE framing: rejected because it is less compatible with OpenAI-oriented clients and intermediaries.

## Decision 3: Separate reasoning text from final answer content at the API contract boundary

- **Decision**: Parse model-emitted reasoning into a dedicated reasoning buffer and expose it separately from final assistant content in both streamed and non-streamed API responses.
- **Rationale**: The feature spec requires the final assistant answer to remain clean while still making reasoning consumable. A separable reasoning field satisfies that requirement more reliably than forcing clients to strip tags out of `message.content`. The parser should still understand `<think>...</think>`-style reasoning text, preserve ordering across streamed fragments, and normalize partial tag boundaries without inventing reasoning content that the model did not emit.
- **Alternatives considered**:
  - Leave reasoning inline inside `content` only: rejected because it pushes cleanup work to every client and weakens the clean-final-answer requirement.
  - Invent a custom opaque reasoning trace disconnected from model output: rejected because the spec explicitly forbids fabricated reasoning.

## Decision 4: Treat reasoning support as manifest- and preset-driven capability metadata

- **Decision**: Keep reasoning support configuration-driven by extending existing preset and/or manifest metadata to describe whether a model path supports incremental streaming and what reasoning format it emits.
- **Rationale**: The committed manifest inventory currently exposes Nemotron as a standard chat model, but nothing in the repository guarantees that the default model emits reasoning text. Capability metadata lets the API, diagnostics, and tests choose supported reasoning-capable configurations without hard-coding a single alias into the runtime. This also satisfies the user request to allow optional model or settings changes when the default model path does not actually produce reasoning output.
- **Alternatives considered**:
  - Hard-code a single reasoning model alias into the API: rejected because the repository’s model policy is manifest-driven, not allowlist-driven.
  - Pretend all chat models support reasoning: rejected because it would fabricate capability and make failures harder to diagnose.

## Decision 5: Keep TurboQuant explicit until it has a real token-stream adapter

- **Decision**: Treat stock MLX as the only streaming-capable runtime path in the initial implementation unless the TurboQuant adapter can emit real token deltas; otherwise the runtime resolver must fail or fall back explicitly before generation starts.
- **Rationale**: The current `TurboRunner` is also a buffered subprocess path. Claiming streaming support there without a token-level adapter would violate the constitution’s experimental-backend safety principle and produce hard-to-debug differences across runtimes.
- **Alternatives considered**:
  - Simulate streamed output for TurboQuant by chunking a completed response: rejected because it hides backend limitations and breaks the real-incremental-generation requirement.
  - Block all streamed requests regardless of backend: rejected because stock MLX can support the requested behavior through `mlx_lm`.

## Decision 6: Use Qwen-style thinking behavior as the normalization target, not a hard dependency

- **Decision**: Design the reasoning parser around common `<think>`-style reasoning output and partial-tag edge cases, but keep the contract generic enough to support any manifest-declared reasoning format later.
- **Rationale**: Public Qwen3 guidance shows practical reasoning quirks the parser must handle, including models that emit reasoning by default, models that can be toggled with `/think` or `enable_thinking=False`, and thinking variants that may emit a closing `</think>` marker without an explicit opening tag in the generated text. Building the contract around normalized reasoning segments rather than one model family keeps the implementation practical without binding the repository to a single upstream.
- **Alternatives considered**:
  - Support only exact `<think>...</think>` pairs: rejected because some reasoning-capable models emit asymmetric markers.
  - Delay reasoning parsing until a specific upstream model is added: rejected because the feature request already requires a reasoning-aware transport contract.

## Sources Consulted

- Local runtime and API sources:
  - `src/local_model/api/server.py`
  - `src/local_model/api/schemas.py`
  - `src/local_model/cli.py`
  - `src/local_model/models.py`
  - `src/local_model/runners/mlx_runner.py`
  - `src/local_model/runners/turbo_runner.py`
  - `src/local_model/services/runtime_resolver.py`
  - `configs/models.yaml`
  - `configs/presets.yaml`
- Installed MLX-LM library inspection:
  - `./.venv/lib/python3.12/site-packages/mlx_lm/__init__.py`
  - `stream_generate(...)` signature and source from the installed `mlx_lm` package
- OpenAI API reference:
  - <https://developers.openai.com/api/reference/resources/chat/subresources/completions/streaming-events>
- Qwen3 reasoning guidance:
  - <https://github.com/QwenLM/Qwen3>
