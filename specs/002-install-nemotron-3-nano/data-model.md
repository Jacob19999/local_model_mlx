# Data Model: Install Nemotron 3 Nano 30B A3B

## Entity: Model Registration

- **Purpose**: Represents the git-safe manifest that makes the installed model discoverable across CLI, API, and UI surfaces.
- **Primary Fields**:
  - `alias`: stable user-facing identifier, recommended example `nemotron-3-nano-30b-a3b`
  - `display_name`: operator-facing name, `Install Nemotron 3 Nano 30B A3B`
  - `source.type`: install source kind, expected to support `hf_repo`, `direct_url`, or `local_dir`
  - `source.location`: upstream repo, URL, or local path
  - `local_path`: cache-relative path for the installed artifact set
  - `default_preset`: default runtime preset, expected to remain `mlx-chat`
  - `runtime`: default runtime family, expected to remain `mlx`
  - `supported_runtimes`: allowed runtime list for this registration
  - `turboquant_compatible`: boolean indicating whether alternate runtime selection is allowed
  - `api_visible`: boolean controlling inclusion in `/v1/models`
  - `tags`: operator-facing descriptors such as `text-generation`, `nemotron`, or `mlx`
  - `notes`: machine-fit or source guidance for operators
- **Validation Rules**:
  - `alias` must be non-empty and unique among registered manifests after slug normalization.
  - `local_path` must resolve to the installed cache location for installed sources.
  - `supported_runtimes` must include `runtime`.
  - `turboquant_compatible = true` must not be emitted unless `supported_runtimes` includes `turboquant`.
  - A registration must not be written until the referenced local artifact set passes install validation.

## Entity: Install Attempt

- **Purpose**: Represents one user-triggered onboarding workflow that acquires, validates, and optionally registers the model.
- **Primary Fields**:
  - `requested_alias`
  - `source_type`
  - `source_location`
  - `destination_path`
  - `copy_files`
  - `default_preset`
  - `status`
  - `error_reason`
- **State Transitions**:
  - `pending -> fetching`
  - `fetching -> validating`
  - `validating -> registered`
  - `pending|fetching|validating -> failed`
- **Validation Rules**:
  - `source_type` must be one of the configured supported source types.
  - `destination_path` must be writable before artifact acquisition begins.
  - Alias conflict checks must run before any existing registration is replaced.
  - Failed attempts must not produce a runnable manifest entry.

## Entity: Runtime Preflight Result

- **Purpose**: Captures the runtime decision shown to the operator before generation begins.
- **Primary Fields**:
  - `requested_runtime`
  - `active_runtime`
  - `fallback_used`
  - `fallback_reason`
  - `notices`
- **Validation Rules**:
  - `active_runtime` must match `requested_runtime` unless a documented fallback is used.
  - Unsupported runtime requests must fail or fall back before token generation starts.
  - Preflight notices must be available to CLI and API consumers for diagnosis.

## Relationships

- A successful **Install Attempt** creates exactly one **Model Registration** for the chosen alias.
- A **Runtime Preflight Result** consumes a **Model Registration** and a requested runtime choice to determine whether the model can run as requested.
- Discovery surfaces (`list-models`, `/v1/models`, UI model lists) read from **Model Registration** only; they never inspect raw cache folders directly.
