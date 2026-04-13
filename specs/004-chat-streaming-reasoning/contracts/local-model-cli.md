# CLI Contract: Streaming Chat Support Through `local-model serve`

## Serve Contract

- **Command**:

```bash
local-model serve [--host 127.0.0.1] [--port 8000]
```

- **Success behavior**:
  - Exit behavior remains the existing service lifecycle behavior.
  - The command exposes both non-streaming and streamed chat-completion behavior through the same local API.
  - Streamed chat requests with `stream: true` are served only when the resolved runtime can emit real incremental output.

- **Failure behavior**:
  - Missing FastAPI, Uvicorn, or runtime dependencies remain blocking startup errors.
  - Runtime-selection failures for a streamed request are surfaced by the API before any stream begins.

## Preset and Runtime Selection Contract

- **Commands**:

```bash
local-model install <alias> ...
local-model register <alias> ...
local-model run <alias> ...
local-model chat <alias> ...
local-model list-models [--json]
```

- **Contract**:
  - No new command family is introduced for streaming or reasoning support.
  - If this feature adds a reasoning-capable preset or manifest metadata, those capabilities are selected through the existing preset and runtime mechanisms.
  - `run` and `chat` remain valid non-streaming smoke surfaces unless a later feature explicitly extends them for interactive streaming.
  - `list-models --json` remains the CLI discovery surface for registered manifests; any capability additions must be backward-compatible.

## Runtime Safety Contract

- **Contract**:
  - Stock MLX remains the default runtime path for the API preset unless an explicitly selected preset or runtime overrides it.
  - Experimental runtime requests must not claim streaming or reasoning capability unless the active adapter can satisfy the same token-level guarantees as stock MLX.
  - When an unsupported streamed runtime is requested and fallback is allowed, the resolved runtime must be explicit in the response metadata and diagnostics. When fallback is disabled, the request must fail before generation begins.
