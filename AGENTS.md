# local_model_mlx Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-12

## Active Technologies

- Python 3.11 runtime with existing SwiftUI shell left unchanged + stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn, optional `huggingface_hub` for `hf_repo` installs, optional `mlx_lm` for stock execution, optional `mlx_turboquant` or `LOCAL_MODEL_TURBO_COMMAND` for alternate-runtime prefligh (002-install-nemotron-3-nano)

## Project Structure

```text
src/
tests/
```

## Commands

cd src && pytest && ruff check .

## Code Style

Python 3.11 runtime with existing SwiftUI shell left unchanged: Follow standard conventions

## Recent Changes

- 002-install-nemotron-3-nano: Added Python 3.11 runtime with existing SwiftUI shell left unchanged + stdlib `argparse` and `subprocess`, FastAPI, Pydantic, Uvicorn, optional `huggingface_hub` for `hf_repo` installs, optional `mlx_lm` for stock execution, optional `mlx_turboquant` or `LOCAL_MODEL_TURBO_COMMAND` for alternate-runtime prefligh

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
