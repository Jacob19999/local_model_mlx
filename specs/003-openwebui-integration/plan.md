# Implementation Plan: Replace macOS UI with Open WebUI

**Branch**: `003-openwebui-integration` | **Date**: 2026-04-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-openwebui-integration/spec.md`

## Summary

Retire the native macOS shell as a maintained product surface, keep `local-model serve` and the existing OpenAI-compatible API as the runtime contract, and replace the operator-facing interactive workflow with documentation-driven Open WebUI onboarding plus CLI and script migration hints for users who still invoke the old UI entry points.

## Technical Context

**Language/Version**: Python 3.11 runtime; repository documentation in Markdown  
**Primary Dependencies**: stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn; Open WebUI is an external UI dependency documented for operators rather than bundled into the runtime  
**Storage**: Git-tracked docs and specs under the repository root and `specs/`; existing model metadata under `configs/` and `models/manifests/`; model artifacts under `models/cache/`  
**Testing**: Targeted `pytest` coverage for CLI behavior changes plus manual smoke validation for `serve`, `/v1/models`, `/v1/chat/completions`, and Open WebUI connection onboarding  
**Target Platform**: Apple Silicon macOS host running the local service with a browser-accessible Open WebUI instance  
**Project Type**: Python CLI plus local API service with documentation-driven external UI integration  
**Performance Goals**: Operators can move from a running local service to a working Open WebUI chat session without changing model registrations or service configuration; migration guidance for the retired UI path is immediate and actionable  
**Constraints**: Keep `local-model serve` and the current API contract intact, delete `apps/macos-ui/` and its launcher assets, avoid adding a second runtime path, and keep the documented primary endpoint at `http://127.0.0.1:8000/v1` for native Open WebUI usage  
**Scale/Scope**: One UI migration for local single-operator workflows; no changes to model manifests, cache layout, or inference backends beyond removing the retired shell surface

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Runtime Ownership**: PASS. Execution remains in the Python runtime under `src/local_model/`, primarily `cli.py` and `api/server.py`. No inference or registry logic moves into a new UI layer.
- **CLI Control Plane**: PASS. `local-model serve` remains the canonical interactive entry point. `local-model ui` and `scripts/launch_ui.sh` are retained only as migration hints that explain the supported Open WebUI workflow and do not launch a second product surface.
- **UI Orchestration Boundary**: CONDITIONAL. The feature intentionally removes `apps/macos-ui/` instead of modifying it. This is a justified product-direction change, but it temporarily conflicts with the constitution’s current assumption that a native shell exists; the deviation is recorded in Complexity Tracking and should be reconciled by a future constitution update if this direction is accepted.
- **Model Artifact Policy**: PASS. No changes are planned for `configs/`, `models/manifests/`, `models/cache/`, or ignore rules. The feature only removes retired UI assets and updates user guidance.
- **Experimental Backend Safety**: PASS. Stock MLX and optional experimental backends continue to operate behind the existing runtime and API. No new backend, fallback, benchmark, or health-check semantics are introduced.

## Project Structure

### Documentation (this feature)

```text
specs/003-openwebui-integration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── local-model-api.md
│   ├── local-model-cli.md
│   └── openwebui-onboarding.md
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
├── doctor.py
├── downloads.py
├── models.py
├── registry.py
├── runners/
│   ├── mlx_runner.py
│   └── turbo_runner.py
└── services/
    ├── diagnostics.py
    ├── install_service.py
    └── runtime_resolver.py

configs/
models/
scripts/
├── bootstrap.sh
└── download_model.sh

tests/
├── contract/
├── integration/
└── unit/

README.md
AGENTS.md
```

**Structure Decision**: Keep the existing single-runtime Python project structure and remove the retired native UI tree from the maintained surface area. Implementation stays in the CLI, API, documentation, and tests; Open WebUI remains an external consumer of the existing API rather than a bundled application inside this repository.

## Post-Design Constitution Check

- **Runtime Ownership**: PASS. Research and contracts keep all execution inside the Python runtime and local API.
- **CLI Control Plane**: PASS. The design documents the unchanged `serve` contract and the redirected `ui` behavior so the CLI remains the place users learn the supported workflow.
- **UI Orchestration Boundary**: CONDITIONAL. The design confirms the native shell is being removed rather than refactored. This remains a justified deviation pending a constitution update if the repository formally adopts the external-UI-only direction.
- **Model Artifact Policy**: PASS. Data model and contracts make no changes to manifests, cache layout, or download recipes.
- **Experimental Backend Safety**: PASS. Open WebUI uses the same existing API contract; runtime fallback behavior remains governed by the current MLX and TurboQuant paths.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Constitution assumes a native shell under `apps/macos-ui/` | This feature intentionally removes the retired native UI to simplify the supported surface and move operators to Open WebUI | Keeping the macOS shell as a maintained surface would contradict the feature goal and continue splitting product attention across two UI paths |
