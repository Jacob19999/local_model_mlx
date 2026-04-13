# Implementation Plan: Install Nemotron 3 Nano 30B A3B

**Branch**: `002-install-nemotron-3-nano` | **Date**: 2026-04-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-install-nemotron-3-nano/spec.md`

## Summary

Add first-party onboarding for Nemotron 3 Nano 30B A3B through the existing `local-model` install, discovery, and run surfaces by treating an MLX-compatible Hugging Face repo as the canonical supported source, validating installs before manifest writes, and documenting the install and runtime-preflight contract so successful installs become immediately runnable on stock MLX.

## Technical Context

**Language/Version**: Python 3.11 runtime with existing SwiftUI shell left unchanged  
**Primary Dependencies**: stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn, optional `huggingface_hub` for `hf_repo` installs, optional `mlx_lm` for stock execution, optional `mlx_turboquant` or `LOCAL_MODEL_TURBO_COMMAND` for alternate-runtime preflight  
**Storage**: Git-tracked JSON/YAML under `configs/` and `models/manifests/`; downloaded model artifacts under `models/cache/`  
**Testing**: Manual CLI and API smoke flows in `quickstart.md`; targeted Python unit and integration coverage should be added under `tests/` for install, registry, and runtime-preflight behavior  
**Target Platform**: Apple Silicon macOS with local filesystem cache  
**Project Type**: Python CLI plus local API service, with a native macOS shell over the same runtime  
**Performance Goals**: One-command install from a supported Hugging Face source, immediate discovery after successful install, no manifest write for failed installs, and user-visible runtime notices before generation starts  
**Constraints**: Keep stock MLX as the default runtime path, add no Nemotron-specific command family, keep weights git-ignored under `models/cache/`, and avoid making a non-MLX or custom-code upstream repo the canonical source for this feature  
**Scale/Scope**: One named 30B-class model onboarding flow, one recommended upstream source, single-user local workflows, and no benchmarking work in this feature

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Runtime Ownership**: PASS. All execution, install, registry, and diagnostics changes stay in the Python runtime under `src/local_model/`, primarily `cli.py`, `downloads.py`, `registry.py`, `services/install_service.py`, `services/runtime_resolver.py`, and `doctor.py`.
- **CLI Control Plane**: PASS. The public surface remains `local-model install`, `local-model list-models`, `local-model run`, and `local-model chat`. No new subcommand or preset is required. Success continues to use the existing text line or `--json` manifest summary, while failures continue to surface on stderr as `error: ...` with non-zero exit status.
- **UI Orchestration Boundary**: PASS. `apps/macos-ui/` remains an orchestrator over the existing API and registry. This feature does not add model-loading logic to the UI.
- **Model Artifact Policy**: PASS. Lightweight source and runtime metadata stay in `configs/` and `models/manifests/`; downloaded model files stay in `models/cache/`. The plan adds model-specific manifest and documentation updates but does not move weights into git-tracked locations.
- **Experimental Backend Safety**: PASS. The feature primarily targets the stock MLX runtime. TurboQuant remains optional, is not assumed compatible for this model by default, and continues to rely on existing preflight and fallback behavior. Validation uses `doctor`, install output, manifest discovery, and runtime banner checks; benchmarking remains out of scope.

## Project Structure

### Documentation (this feature)

```text
specs/002-install-nemotron-3-nano/
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
├── models.yaml
└── presets.yaml

models/
├── cache/
└── manifests/

apps/macos-ui/
scripts/
tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single-runtime Python project structure. Implement model onboarding inside the current CLI, download, registry, and diagnostics modules; keep the API and UI as consumers of the same manifest-driven runtime state; place any new automated coverage under `tests/` grouped by unit, integration, and contract scope.

## Post-Design Constitution Check

- **Runtime Ownership**: PASS. The design keeps Nemotron-specific install logic, validation, and manifest behavior in the Python runtime instead of the UI shell.
- **CLI Control Plane**: PASS. Contracts document the unchanged command family and the expected success and failure outputs for install, listing, and run preflight.
- **UI Orchestration Boundary**: PASS. Quickstart and contracts rely on existing API and CLI surfaces; no alternate UI runtime path is introduced.
- **Model Artifact Policy**: PASS. Data model and research keep model metadata lightweight and model files under `models/cache/`.
- **Experimental Backend Safety**: PASS. Research explicitly chooses an MLX-compatible source and leaves TurboQuant disabled by default unless later compatibility evidence is added.

## Complexity Tracking

No constitutional violations or justified deviations were identified during planning.
