# local_model_mlx Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-12

## Active Technologies
- Python 3.11 runtime; repository documentation in Markdown + stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn; Open WebUI is an external UI dependency documented for operators rather than bundled into the runtime (003-openwebui-integration)
- Git-tracked docs and specs under the repository root and `specs/`; existing model metadata under `configs/` and `models/manifests/`; model artifacts under `models/cache/` (003-openwebui-integration)
- Python 3.11 runtime + stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn, optional `huggingface_hub` for `hf_repo` installs, optional `mlx_lm` for stock execution, optional `mlx_turboquant` or `LOCAL_MODEL_TURBO_COMMAND` for alternate-runtime preflight (002-install-nemotron-3-nano)
- Python 3.11 runtime; repository documentation in Markdown + stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn, optional `mlx_lm` for stock execution and native token streaming, optional `mlx_turboquant` or `LOCAL_MODEL_TURBO_COMMAND` for the alternate runtime path (004-chat-streaming-reasoning)
- Git-tracked configuration under `configs/`, manifest metadata under `models/manifests/`, specs under `specs/`, and ignored model artifacts under `models/cache/` (004-chat-streaming-reasoning)

## Project Structure

```text
src/
tests/
```

## Commands

pytest
ruff check .

## Code Style

Python 3.11 runtime with Open WebUI as the supported interactive surface: Follow standard conventions

## Recent Changes
- 004-chat-streaming-reasoning: Added Python 3.11 runtime; repository documentation in Markdown + stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn, optional `mlx_lm` for stock execution and native token streaming, optional `mlx_turboquant` or `LOCAL_MODEL_TURBO_COMMAND` for the alternate runtime path
- 003-openwebui-integration: Added Python 3.11 runtime; repository documentation in Markdown + stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn; Open WebUI is an external UI dependency documented for operators rather than bundled into the runtime
- 002-install-nemotron-3-nano: Added Python 3.11 runtime + stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn, optional `huggingface_hub` for `hf_repo` installs, optional `mlx_lm` for stock execution, optional `mlx_turboquant` or `LOCAL_MODEL_TURBO_COMMAND` for alternate-runtime preflight

<!-- MANUAL ADDITIONS START -->
- Supported interactive workflow: keep `local-model serve` running and connect Open WebUI to `http://127.0.0.1:8000/v1`.
- `local-model ui` and `scripts/launch_ui.sh` are migration shims only. They print recovery guidance and exit non-zero.
- Verification commands: `curl http://127.0.0.1:8000/health`, `curl http://127.0.0.1:8000/v1/models`, and `local-model list-models --json`.
<!-- MANUAL ADDITIONS END -->
