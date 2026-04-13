# Local Model MLX Workspace

This repository provides a local control plane for Apple Silicon MLX workflows.
The supported interactive path is the local OpenAI-compatible API plus Open WebUI.
The native macOS UI has been retired.

## Supported Surfaces

- `local-model` CLI for install, register, run, chat, doctor, serving, and migration guidance
- stock `mlx_lm` generation for the baseline runtime path
- an optional TurboQuant bridge with explicit fallback behavior
- a local OpenAI-compatible API for Open WebUI and other compatible clients

## Repository Layout

- `src/local_model/`: CLI, runtime selection, runners, registry, diagnostics, API server
- `configs/models.yaml`: supported source types and manifest defaults
- `configs/presets.yaml`: stock and TurboQuant runtime presets
- `models/manifests/`: committed model metadata
- `models/cache/`: downloaded or imported model weights, ignored by git
- `forks/mlx_turboquant/`: optional TurboQuant integration boundary
- `scripts/bootstrap.sh`: editable install plus `doctor`
- `scripts/launch_ui.sh`: migration helper that prints the supported Open WebUI workflow

## Requirements

- Python `>=3.11`
- macOS / Apple Silicon for the intended MLX workflow
- `mlx_lm` installed if you want to run stock MLX generation
- `huggingface_hub` installed if you want `hf_repo` installs
- Open WebUI installed separately if you want the supported browser UI

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

```bash
local-model doctor [--json]
local-model list-models [--json]
local-model install <alias> --source-type {hf_repo,direct_url,local_dir} --source <value> [--copy] [--preset mlx-chat] [--turboquant-compatible] [--json]
local-model register <alias> --path <path> --source-type <type> --source <value> [--preset mlx-chat] [--turboquant-compatible] [--notes <text>] [--json]
local-model run <alias> [--prompt "..."] [--preset <name>] [--runtime {mlx,turboquant}] [--no-fallback] [--json]
local-model chat <alias> [--prompt "..."] [--preset <name>] [--runtime {mlx,turboquant}] [--no-fallback] [--json]
local-model serve [--host 127.0.0.1] [--port 8000]
local-model ui [--api-base-url http://127.0.0.1:8000]
```

Notes:

- `run` and `chat` share the same generation flow today.
- If `--prompt` is omitted, the CLI reads from stdin or prompts interactively.
- `local-model ui` is a migration notice for the retired native UI path. It prints the supported Open WebUI workflow and exits non-zero.
- `./scripts/launch_ui.sh` is the shell equivalent of that migration notice.

## Open WebUI Onboarding

1. Ensure at least one model is registered:

```bash
local-model list-models --json
```

2. Start the local API:

```bash
local-model serve --host 127.0.0.1 --port 8000
```

3. Verify the service before opening Open WebUI:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/models
```

4. Start Open WebUI on the same machine:

```bash
python -m pip install open-webui
open-webui serve
```

5. In Open WebUI, add an OpenAI-compatible connection with:

- API URL: `http://127.0.0.1:8000/v1`
- API key: blank or `none`

If Open WebUI runs in Docker while `local-model serve` runs on the host, use
`http://host.docker.internal:8000/v1` instead.

6. Pick a discovered model and send a test prompt.

## Troubleshooting

- Service unavailable: run `curl http://127.0.0.1:8000/health` and restart `local-model serve` if it fails.
- No models visible in Open WebUI: run `curl http://127.0.0.1:8000/v1/models` and `local-model list-models --json` to confirm at least one API-visible manifest is registered.
- Wrong endpoint configured: replace it with `http://127.0.0.1:8000/v1` for native Open WebUI or `http://host.docker.internal:8000/v1` for Dockerized Open WebUI on the same host.
- Legacy UI commands used by habit: run `local-model ui` or `./scripts/launch_ui.sh` and follow the printed migration notice instead of expecting a launched app.

## Validation Notes

Validation recorded on 2026-04-12:

- `./.venv/bin/python -m pytest` passed with `23 passed`.
- `./.venv/bin/python -m local_model ui` printed the Open WebUI migration notice and exited non-zero as intended.
- `./scripts/launch_ui.sh` printed the shell migration helper output and exited non-zero as intended.
- The browser-side Open WebUI connection remains an operator-run smoke flow because Open WebUI is an external dependency rather than a bundled repo service.

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
