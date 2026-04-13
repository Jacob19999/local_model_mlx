# Implementation Plan: Add streaming chat completions with reasoning output

**Branch**: `004-chat-streaming-reasoning` | **Date**: 2026-04-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-chat-streaming-reasoning/spec.md`

## Summary

Extend the existing local OpenAI-compatible chat endpoint so `stream: true`
produces real incremental server-sent deltas from the runner layer, preserve the
current non-streaming response path, and add a reasoning-aware parsing contract
that keeps final assistant content clean while exposing model-emitted reasoning
only when a supported model or preset actually produces it.

## Technical Context

**Language/Version**: Python 3.11 runtime; repository documentation in Markdown  
**Primary Dependencies**: stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn, optional `mlx_lm` for stock execution and native token streaming, optional `mlx_turboquant` or `LOCAL_MODEL_TURBO_COMMAND` for the alternate runtime path  
**Storage**: Git-tracked configuration under `configs/`, manifest metadata under `models/manifests/`, specs under `specs/`, and ignored model artifacts under `models/cache/`  
**Testing**: Targeted `pytest` unit, contract, and integration coverage for runner streaming, API streaming, reasoning parsing, and runtime fallback behavior; manual `curl -N` smoke validation for streamed chat  
**Target Platform**: Apple Silicon macOS host running the local API service  
**Project Type**: Python CLI plus local OpenAI-compatible API service  
**Performance Goals**: Streamed requests emit visible deltas before full completion, non-streamed requests retain current single-response behavior, and reasoning parsing preserves generation order without buffering the full response before first output  
**Constraints**: No fake streaming from buffered subprocess output, no new endpoint family, no committed model weights, explicit fallback or failure when the selected runtime cannot stream incrementally, and no fabricated reasoning content for non-reasoning models  
**Scale/Scope**: One existing API endpoint, additive request and response fields, one runner abstraction expansion for streaming, and optional manifest or preset metadata changes to identify reasoning-capable configurations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Runtime Ownership**: PASS. Execution stays in the Python runtime under `src/local_model/`, primarily `api/server.py`, `api/schemas.py`, `cli.py`, `models.py`, `runners/base.py`, `runners/mlx_runner.py`, `runners/turbo_runner.py`, and `services/runtime_resolver.py`.
- **CLI Control Plane**: PASS. The public control plane remains `local-model serve`, `install`, `register`, `list-models`, `run`, and `chat`. No new command family is required. The feature may add a preset or manifest capability metadata, but those remain within the existing control plane and config surfaces.
- **UI Orchestration Boundary**: PASS. No UI code or separate runtime path is introduced. Existing consumers such as Open WebUI continue to call the local API only.
- **Model Artifact Policy**: PASS. No changes are planned for `models/cache/` or ignore rules. If reasoning capability metadata is needed, it stays in `configs/` and `models/manifests/`.
- **Experimental Backend Safety**: PASS. Stock MLX is the primary streaming path. The TurboQuant path must either add a true token-stream adapter later or fail or fall back explicitly; the plan does not allow simulated streaming for unsupported backends.

## Project Structure

### Documentation (this feature)

```text
specs/004-chat-streaming-reasoning/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── local-model-api.md
│   └── local-model-cli.md
└── tasks.md
```

### Source Code (repository root)

```text
src/local_model/
├── api/
│   ├── schemas.py
│   └── server.py
├── cli.py
├── config.py
├── models.py
├── registry.py
├── runners/
│   ├── base.py
│   ├── mlx_runner.py
│   └── turbo_runner.py
└── services/
    ├── diagnostics.py
    └── runtime_resolver.py

configs/
├── models.yaml
└── presets.yaml

models/
├── cache/
└── manifests/

tests/
├── contract/
├── integration/
└── unit/

README.md
```

**Structure Decision**: Keep the existing single-runtime Python project structure. Implement streamed generation and reasoning parsing in the runtime and API layers, use config and manifest metadata for capability discovery, and add validation under the existing `tests/` split by unit, contract, and integration scope.

## Post-Design Constitution Check

- **Runtime Ownership**: PASS. Research and data model keep generation, parsing, and streaming inside the Python runtime and do not push any execution responsibility to external UIs.
- **CLI Control Plane**: PASS. Contracts keep `local-model serve` as the public entry point for API behavior and limit any capability selection to existing preset and manifest mechanisms.
- **UI Orchestration Boundary**: PASS. The design changes only the local API behavior consumed by clients; no UI orchestration changes are required.
- **Model Artifact Policy**: PASS. Planned metadata additions are git-safe and limited to tracked config or manifest files; cache layout remains unchanged.
- **Experimental Backend Safety**: PASS. The design explicitly requires true incremental emission for any runtime that claims streaming support and preserves explicit fallback or failure semantics when that guarantee cannot be met.

## Complexity Tracking

No constitutional violations or justified deviations were identified during planning.
