# Repo Plan

## Goal

Build a macOS-first local LLM workspace that can:

- run an MLX-based TurboQuant fork for Apple Silicon experiments
- download and organize models inside this repo
- expose multiple named CLI commands for different runtimes and presets
- launch a modern MLX-style UI for chat and model control

This repo is currently empty, so the plan below assumes a greenfield setup.

## Product Shape

The project should have 3 layers:

1. A Python runtime layer for model download, MLX execution, and TurboQuant experiments.
2. A command layer that gives you stable CLI entrypoints such as `download`, `run`, `chat`, `bench`, and `ui`.
3. A macOS UI layer that launches and controls those commands, rather than duplicating inference logic.

This split keeps the fast-moving model/runtime work in Python while letting the app stay focused on UX.

## Recommended Architecture

### 1. Runtime Layer

Use Python for the core execution pipeline:

- base runtime: `mlx`, `mlx-lm`, and optionally `mlx-vlm`
- TurboQuant path: a forked or vendored runtime under this repo
- model registry: local metadata describing model id, source, format, tags, and preferred launch command
- job runner: one process API for spawning generation, streaming logs, and collecting metrics

Why this split:

- MLX Python is the easiest place to integrate a custom TurboQuant path.
- model download and conversion workflows are simpler to automate in Python
- benchmarking and experimenting with multiple CLI shapes is much faster outside the UI app

### 2. CLI Layer

Create one top-level CLI with subcommands instead of many unrelated scripts.

Suggested commands:

- `local-model download <model-alias>`
- `local-model list-models`
- `local-model run <model-alias>`
- `local-model chat <model-alias>`
- `local-model bench <model-alias>`
- `local-model ui`
- `local-model doctor`

Suggested runtime presets:

- `mlx-chat`: normal chat generation
- `mlx-bench`: prompt and decode benchmarking
- `mlx-turbo`: TurboQuant-enabled generation path
- `mlx-vision`: multimodal path when the model supports it

The CLI should be the single source of truth. The UI can call the same commands internally.

### 3. UI Layer

Target a native macOS SwiftUI app that feels like a modern MLX app.

Best practical approach:

- use the official MLX Swift ecosystem as the UI foundation
- borrow UX ideas or structure from `MLXChatExample` in `ml-explore/mlx-swift-examples`
- treat the UI as an app shell over the Python runtime first

The UI should provide:

- model picker
- download progress
- runtime preset picker
- prompt/chat screen
- terminal/log stream panel
- benchmark screen with tokens per second and memory notes
- quick launch buttons for common commands

## Repo Structure

Suggested initial layout:

```text
.
├── PLAN.md
├── README.md
├── pyproject.toml
├── src/
│   └── local_model/
│       ├── cli.py
│       ├── config.py
│       ├── registry.py
│       ├── downloads.py
│       ├── runners/
│       │   ├── mlx_runner.py
│       │   ├── turbo_runner.py
│       │   └── bench_runner.py
│       └── services/
│           ├── process_manager.py
│           └── metrics.py
├── configs/
│   ├── models.yaml
│   └── presets.yaml
├── models/
│   ├── manifests/
│   └── cache/
├── forks/
│   └── mlx_turboquant/
├── scripts/
│   ├── bootstrap.sh
│   ├── download_model.sh
│   └── launch_ui.sh
├── apps/
│   └── macos-ui/
└── tests/
```

Notes:

- `models/cache/` stores downloaded weights and should not be committed.
- `models/manifests/` can store lightweight metadata files that are safe to commit.
- `forks/mlx_turboquant/` keeps the custom runtime isolated from app code.

## Model Strategy

Store models in this repo, but do not put the heavy files in git.

Plan:

- commit only manifests and download recipes
- keep weights under `models/cache/`
- support at least these source types:
  - Hugging Face repo
  - direct file URL
  - local imported model directory
- track for each model:
  - alias
  - upstream id
  - runtime type: `mlx`, `gguf`, `vision`, `turbo`
  - local path
  - default command preset
  - notes about memory fit on your machine

For your machine, prioritize MLX-friendly Gemma and Qwen models first.

## TurboQuant Integration Plan

Important assumption:

Google's official TurboQuant work is centered on KV-cache compression, while your goal sounds broader: a local MLX fork that you can run directly from this repo. That means we should plan for experimental integration, not assume a drop-in upstream MLX feature.

Recommended approach:

1. Start with a working stock MLX path first.
2. Add a forked runtime under `forks/mlx_turboquant/`.
3. Define one narrow adapter interface in the main app:
   - `download_model()`
   - `load_model()`
   - `generate()`
   - `stream_generate()`
   - `benchmark()`
4. Implement both a stock MLX runner and a TurboQuant runner behind that interface.
5. Keep the TurboQuant fork optional so the repo still works when that path is unavailable or unstable.

This avoids coupling the whole product to the experimental branch.

## Milestones

### Phase 1: Foundation

- create Python package and top-level CLI
- add config files for models and presets
- add model download support into `models/cache/`
- add a stock MLX chat/run path
- add `doctor` command for environment checks

Definition of done:

- you can run `local-model download ...`
- you can run `local-model chat ...`
- models are stored in this repo in a predictable layout

### Phase 2: TurboQuant Runtime

- add `forks/mlx_turboquant/`
- wrap the fork with a stable runner module
- add a `mlx-turbo` preset
- add a benchmark command that compares stock MLX vs TurboQuant

Definition of done:

- one model can run through both stock and TurboQuant paths
- the CLI can switch between them with a flag or preset
- output reports include speed and failure diagnostics

### Phase 3: Modern UI

- scaffold a macOS SwiftUI app in `apps/macos-ui/`
- implement model picker, logs, and chat screen
- launch CLI jobs from the app and stream output back into the UI
- persist recent models, prompts, and presets

Definition of done:

- opening the app lets you select a model and launch a local run
- downloads and generation can be started from the UI
- the app can open a terminal/log drawer for debugging

### Phase 4: UX and Packaging

- add one-click bootstrap
- add richer benchmark views
- add import/export of model manifests
- package the macOS app for local use

Definition of done:

- fresh clone to first prompt is simple
- runtime errors are understandable
- the app feels like the primary entrypoint, not a thin demo

## First Build Order

If we implement this incrementally, I would build in this order:

1. `pyproject.toml` and Python package skeleton
2. `configs/models.yaml` and `configs/presets.yaml`
3. `download` and `doctor` commands
4. stock `mlx` runner
5. `bench` command
6. TurboQuant fork integration
7. SwiftUI macOS shell that launches the CLI

This gives us a usable product early and keeps the experimental work from blocking the whole repo.

## Risks

- TurboQuant support may require custom patches that do not map cleanly onto upstream MLX APIs.
- some model families may need separate code paths for text-only versus multimodal behavior
- storing models inside the repo can consume large disk space quickly without cache cleanup rules
- a native Swift UI that embeds inference directly would increase complexity a lot compared with a CLI-backed UI

## Decisions I Recommend Up Front

- use Python as the runtime control plane
- use SwiftUI for the macOS app
- keep model files under `models/cache/`
- keep the TurboQuant fork isolated under `forks/`
- make the UI call the same CLI that terminal users call

## Immediate Next Step

Start Phase 1 and scaffold the repo so there is one working stock MLX path before touching TurboQuant.
