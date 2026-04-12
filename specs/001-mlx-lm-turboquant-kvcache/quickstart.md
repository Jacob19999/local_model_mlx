# Quickstart

These smoke flows are intentionally minimal. Benchmarking is out of scope for this
feature.

## Doctor Check

```bash
PYTHONPATH=src python -m local_model doctor
```

Expected outcome:

- config and cache directories resolve correctly
- missing optional dependencies are reported as `warn`, not silent failures
- TurboQuant availability is reported before the user tries to run it

## User Story 1: Alias Switching

1. Register two model aliases:
   `PYTHONPATH=src python -m local_model register alpha --path /path/to/alpha --source-type local_dir --source /path/to/alpha`
   `PYTHONPATH=src python -m local_model register beta --path /path/to/beta --source-type local_dir --source /path/to/beta`
2. Confirm both appear in `PYTHONPATH=src python -m local_model list-models`.
3. Run the same command family against each alias:
   `PYTHONPATH=src python -m local_model run alpha --prompt "hello"`
   `PYTHONPATH=src python -m local_model run beta --prompt "hello"`
4. Confirm only the alias input changed and the runtime banner identifies the selected model before generation.

## User Story 2: Install and Register

1. Install a supported model:
   `PYTHONPATH=src python -m local_model install qwen25 --source-type hf_repo --source mlx-community/Qwen2.5-1.5B-Instruct-4bit`
2. Confirm `models/manifests/qwen25.yaml` exists and `models/cache/qwen25/` is populated.
3. Confirm `PYTHONPATH=src python -m local_model list-models` shows the new alias.
4. Target it through the existing run flow.

## User Story 3: TurboQuant Path

1. Ensure the manifest declares TurboQuant compatibility and either `LOCAL_MODEL_TURBO_COMMAND` or `mlx_turboquant` is available.
2. Run:
   `PYTHONPATH=src python -m local_model run qwen25 --runtime turboquant --prompt "Explain the active runtime."`
3. Confirm the runtime banner reports `requested_runtime: turboquant` and `active_runtime: turboquant` before generation starts.

## User Story 4: Safe Fallback

1. Request TurboQuant for a manifest without compatibility or on a machine without the optional runtime:
   `PYTHONPATH=src python -m local_model run alpha --runtime turboquant --prompt "fallback?"`
2. Confirm the CLI prints a fallback or actionable failure message before generation.
3. Re-run with `--no-fallback` and confirm the command stops before generation.

## User Story 5: UI and API

1. Start the API:
   `PYTHONPATH=src python -m local_model serve --host 127.0.0.1 --port 8000`
2. In another terminal, list models through the API:
   `curl http://127.0.0.1:8000/v1/models`
3. Send an OpenAI-compatible request:
   `curl -X POST http://127.0.0.1:8000/v1/chat/completions -H 'content-type: application/json' -d '{"model":"qwen25","messages":[{"role":"user","content":"Hello"}]}'`
4. Launch the UI shell:
   `./scripts/launch_ui.sh`
5. Confirm the SwiftUI shell shows the registered models and the current runtime state from the same API.

## End-to-End Smoke

1. Run `doctor`.
2. Install or register a model.
3. Launch stock MLX through `run`.
4. Attempt a TurboQuant run and confirm either success or explicit fallback.
5. Start the API and confirm `/v1/models` shows the same registered aliases.
6. Launch the SwiftUI shell and confirm it reflects the same registry.
