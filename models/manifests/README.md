# Model Manifests

Use manifests to declare which models are supported by the CLI, API, and UI.
Downloaded or imported weights stay under `models/cache/`, but those cache folders
are invisible until a manifest is present.

## Registration Rules

- Use `local-model install` to download or import a model and write a manifest.
- Use `local-model register` when weights already exist locally.
- Do not hand-edit cache paths without updating the manifest.
- Do not expose raw cache directories through the runtime surfaces.

## Required Fields

- `alias`: stable user-facing name used by CLI, API, and UI
- `source.type`: `hf_repo`, `direct_url`, or `local_dir`
- `source.location`: upstream ID, URL, or local directory path
- `local_path`: directory or file location used by the runtime
- `default_preset`: default preset such as `mlx-chat`
- `supported_runtimes`: allowed runtime list, for example `["mlx"]`
- `turboquant_compatible`: whether the TurboQuant adapter may be selected

## Fallback Policy

- Requests that ask for TurboQuant on a manifest without `turboquant_compatible`
  fail preflight unless the chosen preset allows fallback.
- When fallback is allowed, the resolver switches the session to stock MLX and
  records the fallback reason before generation begins.
- Invalid manifests stop the session before generation with actionable errors.

## Template

Start from `models/manifests/template.yaml` and either commit the new manifest
directly or let `local-model register` create it for you.

