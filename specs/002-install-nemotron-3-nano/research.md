# Research: Install Nemotron 3 Nano 30B A3B

## Decision 1: Use an MLX-formatted Hugging Face repo as the canonical supported source

- **Decision**: Treat `hf_repo` installation from `lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit` as the canonical first-party source for this feature.
- **Rationale**: The current runtime executes `mlx_lm.generate` against a local model directory, and the existing `install_from_hf_repo()` flow downloads a full Hugging Face snapshot into `models/cache/<alias>/`. The LM Studio community variant is explicitly tagged `mlx`, which aligns with the stock MLX runner. By contrast, NVIDIA's BF16 and FP8 repos are tagged for `transformers` and include custom model code, so they are not the lowest-risk fit for this repository's stock MLX execution path. Preferring the 4-bit MLX variant is an inference from the available MLX repo options and the local Apple Silicon target: it is the most practical default among the published MLX variants for a first supported install path.
- **Alternatives considered**:
  - `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`: rejected as the canonical path because it is not presented as an MLX repo and would require a different execution path than the current runner.
  - `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8`: rejected for the same reason.
  - `lmstudio-community/...-MLX-5bit` and `...-MLX-6bit`: valid future alternatives, but not the default recommendation for the first supported path.
  - `local_dir` or `direct_url`: remain supported input types, but they are not the recommended first-party onboarding path for this model.

## Decision 2: Keep the public surface on existing commands and manifests

- **Decision**: Do not add Nemotron-specific commands, presets, or API endpoints. Use the existing `local-model install`, `list-models`, `run`, `chat`, and `/v1/models` surfaces.
- **Rationale**: The CLI already exposes alias-driven install and runtime selection, and the API and UI already consume manifest-driven discovery. The constitution requires one CLI control plane and manifest-backed model onboarding, so the safest design is to extend current behaviors rather than forking them.
- **Alternatives considered**:
  - New `local-model install-nemotron` command: rejected because it fractures the control plane.
  - Hard-coded Nemotron handling in the UI or API only: rejected because it bypasses the shared runtime contract.

## Decision 3: Validate install completion before manifest write and block alias collisions

- **Decision**: Add an explicit validation boundary between acquiring artifacts and writing the manifest, and fail early when an alias already points to a different registered model.
- **Rationale**: The current install flow creates or reuses a cache destination and then immediately writes manifest data. For a large remote model, partial downloads or interrupted installs can leave on-disk artifacts that look populated while still being incomplete. A validation step is needed so failed installs do not become discoverable. Alias-collision handling is also required so a new install cannot silently replace an existing registered model definition.
- **Alternatives considered**:
  - Register immediately after `snapshot_download()` returns with no additional checks: rejected because incomplete or conflicting state becomes harder to diagnose.
  - Allow last-write-wins alias replacement: rejected because it violates the spec's safe-failure requirement.

## Decision 4: Keep model-specific behavior in manifest data, not hard-coded allowlists

- **Decision**: Store the recommended source, runtime support, display name, and operator-facing notes for this model in manifest and documentation data instead of hard-coding them into CLI control flow.
- **Rationale**: Registry discovery, API listing, and runtime preflight already depend on manifest fields such as `alias`, `source`, `supported_runtimes`, and `turboquant_compatible`. Keeping Nemotron-specific support in manifests and docs preserves the repository's model-artifact policy and keeps future model additions consistent with the same contract.
- **Alternatives considered**:
  - A hard-coded Nemotron allowlist in `cli.py` or `registry.py`: rejected because it couples one model to code paths that should remain manifest-driven.

## Decision 5: Validate through doctor, install smoke flows, and runtime preflight rather than benchmarks

- **Decision**: Use `doctor`, CLI JSON output, manifest discovery, API listing, and run preflight checks as the validation plan for this feature.
- **Rationale**: This feature is about safe onboarding of one model, not about performance claims. The repository does not currently include an automated test harness, so the plan should center on explicit smoke workflows and targeted service-level checks rather than benchmark work.
- **Alternatives considered**:
  - Benchmarking Nemotron throughput or memory fit: rejected because the spec keeps benchmarking out of scope.
  - Requiring UI-specific validation only: rejected because the CLI is the public control plane.

## Sources Consulted

- Hugging Face model metadata for the official BF16 repo: <https://hf.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16>
- Hugging Face model metadata for the official FP8 repo: <https://hf.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8>
- Hugging Face model metadata for the MLX 4-bit repo: <https://hf.co/lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit>
- Hugging Face model metadata for the MLX 5-bit repo: <https://hf.co/lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-5bit>
- Hugging Face model metadata for the MLX 6-bit repo: <https://hf.co/lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit>
