# Local Model MLX Workspace

This repository provides one local control plane for:

- registering and installing models into `models/cache/`
- running stock MLX generation flows from the `local-model` CLI
- opting into an experimental TurboQuant path with clear fallback notices
- exposing the same registry through a local OpenAI-compatible API
- launching a plain macOS SwiftUI shell that observes the same runtime state

## Layout

- `src/local_model/`: Python runtime, CLI, diagnostics, API server, and runners
- `configs/`: committed runtime and source metadata
- `models/manifests/`: lightweight model manifests committed to git
- `models/cache/`: ignored downloaded or imported weights
- `forks/mlx_turboquant/`: optional experimental backend integration boundary
- `apps/macos-ui/`: plain SwiftUI shell that calls the local API

## Bootstrap

```bash
./scripts/bootstrap.sh
```

The bootstrap script creates a virtual environment, installs the package in editable
mode, and runs `local-model doctor`.

## CLI

```bash
local-model doctor
local-model list-models
local-model register demo --path /path/to/model --source-type local_dir --source /path/to/model
local-model install qwen25 --source-type hf_repo --source mlx-community/Qwen2.5-1.5B-Instruct-4bit
local-model run qwen25 --prompt "Summarize TurboQuant fallback behavior."
local-model run qwen25 --runtime turboquant --prompt "Explain the active runtime."
local-model chat qwen25
local-model serve --host 127.0.0.1 --port 8000
local-model ui
```

## Runtime Behavior

- `mlx-chat` is the default preset for stock MLX generation.
- `mlx-turbo` requests the TurboQuant path and falls back to stock MLX when the
  preset allows fallback and the manifest/runtime is incompatible.
- `local-model doctor` reports Python version, optional dependency visibility,
  cache and config paths, registered manifests, and TurboQuant availability.

## API

The local API is OpenAI-compatible for the minimal discovery and chat flow:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`

The chat endpoint returns the selected model, the requested runtime, the active
runtime, and a non-streaming completion payload.

## Model Policy

- Keep only manifests and presets under version control.
- Keep weights and imported model directories under `models/cache/`.
- Register models through `local-model install` or `local-model register`.
- Raw folders under `models/cache/` are ignored until a manifest exists.

See [models/manifests/README.md](models/manifests/README.md) for manifest fields
and registration rules.

