# MLX TurboQuant Integration Boundary

This directory isolates the optional experimental runtime from the stock MLX path.

## Intended Contract

The adapter in `src/local_model/runners/turbo_runner.py` expects the fork to expose
an executable or module capable of:

- loading a model from `models/cache/<alias>/`
- generating text for a prompt
- failing fast when the runtime or the manifest is incompatible

## Current Status

No forked runtime is vendored yet. Set one of these integration points once the
fork is available:

- `LOCAL_MODEL_TURBO_COMMAND`, pointing to an executable command
- a Python module importable as `mlx_turboquant`

Until then, TurboQuant requests either fall back to stock MLX when the preset
allows it or fail during preflight with an actionable diagnostic.

