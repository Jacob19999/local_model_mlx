# CLI Contract: Nemotron 3 Nano 30B A3B Onboarding

## Install Contract

- **Command**:

```bash
local-model install <alias> --source-type hf_repo --source <hugging-face-repo> [--preset mlx-chat] [--json]
```

- **Canonical example**:

```bash
local-model install nemotron-3-nano-30b-a3b \
  --source-type hf_repo \
  --source lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit \
  --json
```

- **Success behavior**:
  - Exit code `0`
  - Text mode prints `Installed and registered <alias> at <local_path>`
  - JSON mode returns:
    - `alias`
    - `display_name`
    - `source_type`
    - `source`
    - `local_path`
    - `default_preset`
    - `runtime`
    - `supported_runtimes`
    - `turboquant_compatible`
    - `api_visible`
    - `tags`
    - `notes`

- **Failure behavior**:
  - Non-zero exit code
  - stderr format `error: <message>`
  - Required failure cases:
    - missing `huggingface_hub`
    - unreachable or unauthorized source repo
    - incomplete or invalid downloaded artifact set
    - alias conflict with an existing different registration
    - unwritable cache or manifest destination
  - Alias-conflict failures must leave the existing manifest untouched.

## Discovery Contract

- **Command**:

```bash
local-model list-models [--json]
```

- **Success behavior**:
  - Exit code `0`
  - Newly installed Nemotron alias appears immediately after successful registration
  - JSON output includes the manifest summary fields above, including `runtime`

## Run and Chat Preflight Contract

- **Commands**:

```bash
local-model run <alias> [--runtime {mlx,turboquant}] [--no-fallback] [--json]
local-model chat <alias> [--runtime {mlx,turboquant}] [--no-fallback] [--json]
```

- **Success behavior**:
  - Runtime banner prints:
    - `model: <alias>`
    - `requested_runtime: <runtime>`
    - `active_runtime: <runtime>`
  - JSON mode returns a generation payload containing `model_alias`, `requested_runtime`, `active_runtime`, `output_text`, `command`, and optional `fallback_reason`

- **Failure behavior**:
  - Unsupported runtime requests must fail before generation when fallback is disabled
  - The error must identify the incompatibility or missing optional runtime
  - Interrupted installs and invalid manifests must never surface as runnable aliases
