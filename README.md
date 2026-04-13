# Local Model MLX Workspace

This repository provides a local control plane for Apple Silicon MLX workflows.
It combines one model registry with four operator surfaces:

- `local-model` CLI for install, register, run, chat, doctor, API, and UI launch
- stock `mlx_lm` generation for the baseline runtime path
- an optional TurboQuant bridge with explicit fallback behavior
- a local OpenAI-compatible API and a plain macOS SwiftUI shell

## What It Does

- installs or registers models into `models/cache/`
- keeps lightweight manifests under `models/manifests/`
- lets you switch model aliases without changing command families
- exposes the same registry to CLI, API, and UI clients
- reports whether a request is running on stock MLX, TurboQuant, or a fallback path

## Repository Layout

- `src/local_model/`: CLI, runtime selection, runners, registry, diagnostics, API server
- `configs/models.yaml`: supported source types and manifest defaults
- `configs/presets.yaml`: stock and TurboQuant runtime presets
- `models/manifests/`: committed model metadata
- `models/cache/`: downloaded or imported model weights, ignored by git
- `forks/mlx_turboquant/`: optional TurboQuant integration boundary
- `apps/macos-ui/`: SwiftUI shell backed by the local API
- `scripts/bootstrap.sh`: editable install plus `doctor`
- `scripts/launch_ui.sh`: SwiftUI launcher

## Requirements

- Python `>=3.11`
- macOS / Apple Silicon for the intended MLX workflow
- `mlx_lm` installed if you want to run stock MLX generation
- `huggingface_hub` installed if you want `hf_repo` installs
- Swift / Xcode if you want to launch the macOS UI

The package itself currently installs:

- `fastapi`
- `pydantic`
- `uvicorn`

## Bootstrap

Create a virtual environment, install the package in editable mode, and run the
environment checks:

```bash
./scripts/bootstrap.sh
```

Manual equivalent:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m local_model doctor
```

## First Run

Register an existing local model directory:

```bash
local-model register demo \
  --path /path/to/model \
  --source-type local_dir \
  --source /path/to/model
```

Or install from Hugging Face:

```bash
local-model install nemotron-3-nano-30b-a3b \
  --source-type hf_repo \
  --source lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit \
  --json
```

Then list and run:

```bash
local-model list-models
local-model run nemotron-3-nano-30b-a3b --prompt "Summarize the active runtime."
```

## CLI Reference

Core commands:

```bash
local-model doctor
local-model list-models [--json]
local-model install <alias> --source-type {hf_repo,direct_url,local_dir} --source <value> [--copy] [--preset mlx-chat] [--turboquant-compatible]
local-model register <alias> --path <path> --source-type <type> --source <value> [--preset mlx-chat] [--turboquant-compatible]
local-model run <alias> [--prompt "..."] [--preset <name>] [--runtime {mlx,turboquant}] [--no-fallback]
local-model chat <alias> [--prompt "..."] [--preset <name>] [--runtime {mlx,turboquant}] [--no-fallback]
local-model serve [--host 127.0.0.1] [--port 8000]
local-model ui [--api-base-url http://127.0.0.1:8000]
```

Notes:

- `run` and `chat` share the same generation flow today.
- If `--prompt` is omitted, the CLI reads from stdin or prompts interactively.
- `--json` is available on `doctor`, `list-models`, `install`, `register`, `run`, and `chat`.
- `install --copy` copies a local directory into `models/cache/<alias>/`; without it,
  local directory installs use a symlink.

## Runtime Presets

Configured in [configs/presets.yaml](/Users/Apple/Documents/local_model_mlx/configs/presets.yaml):

- `mlx-chat`: stock MLX runtime, no fallback
- `mlx-turbo`: requests TurboQuant and allows fallback to stock MLX
- `mlx-api`: stock MLX defaults used by the local API

You can either pick a preset with `--preset` or override runtime choice directly
with `--runtime`.

## Stock MLX and TurboQuant

Stock MLX calls:

```bash
python -m mlx_lm.generate --model <resolved-model-path> --prompt <prompt> --max-tokens <n>
```

TurboQuant is intentionally optional. The bridge in
[src/local_model/runners/turbo_runner.py](/Users/Apple/Documents/local_model_mlx/src/local_model/runners/turbo_runner.py)
looks for:

- `LOCAL_MODEL_TURBO_COMMAND`, pointing to an executable command
- or an importable `mlx_turboquant` runtime once that integration exists

Example:

```bash
export LOCAL_MODEL_TURBO_COMMAND="/path/to/turboquant-generate"
local-model run qwen25 --runtime turboquant --prompt "Explain the active runtime."
```

If TurboQuant is requested for an incompatible manifest or the runtime is not
available, the resolver either:

- falls back to stock MLX when the active preset allows it
- or stops before generation with an actionable error

## API

Start the local OpenAI-compatible API:

```bash
local-model serve --host 127.0.0.1 --port 8000
```

Implemented endpoints:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`

Examples:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/models
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"qwen25","messages":[{"role":"user","content":"Hello"}]}'
```

The chat response includes the selected model plus runtime metadata for the
resolved session.

## macOS UI

Launch the SwiftUI shell:

```bash
local-model ui
```

Or directly:

```bash
./scripts/launch_ui.sh
```

The UI expects Swift to be installed and reads the API base URL from
`LOCAL_MODEL_API_BASE_URL` when present.

## Model Manifests and Cache Policy

Model weights and imported directories belong under `models/cache/`. Git-tracked
metadata belongs under `models/manifests/`.

Rules:

- use `local-model install` or `local-model register` to create manifests
- keep raw weights out of git
- do not treat arbitrary cache folders as registered models
- mark TurboQuant support per manifest, not by cache-folder convention
- let install validation fail before manifest writes when artifacts are incomplete
- treat alias conflicts as blocking errors unless the alias already points to the same source

Example manifest:

```json
{
  "alias": "nemotron-3-nano-30b-a3b",
  "display_name": "Install Nemotron 3 Nano 30B A3B",
  "source": {
    "type": "hf_repo",
    "location": "lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit"
  },
  "local_path": "models/cache/nemotron-3-nano-30b-a3b",
  "default_preset": "mlx-chat",
  "runtime": "mlx",
  "supported_runtimes": ["mlx"],
  "turboquant_compatible": false,
  "api_visible": true,
  "tags": ["text-generation", "nemotron", "mlx"]
}
```

See [models/manifests/README.md](/Users/Apple/Documents/local_model_mlx/models/manifests/README.md)
for registration rules and required fields.

## Smoke Flow

Minimal end-to-end sequence:

```bash
local-model doctor
local-model install nemotron-3-nano-30b-a3b \
  --source-type hf_repo \
  --source lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit
local-model run nemotron-3-nano-30b-a3b --prompt "Hello"
local-model run nemotron-3-nano-30b-a3b --runtime turboquant --no-fallback --prompt "Explain the runtime"
local-model serve
local-model ui
```

More explicit story-based smoke steps live in
[specs/001-mlx-lm-turboquant-kvcache/quickstart.md](/Users/Apple/Documents/local_model_mlx/specs/001-mlx-lm-turboquant-kvcache/quickstart.md).
