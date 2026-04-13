# CLI Contract: Open WebUI Migration

## Serve Contract

- **Command**:

```bash
local-model serve [--host 127.0.0.1] [--port 8000]
```

- **Success behavior**:
  - Exit code remains the existing service lifecycle behavior.
  - The command starts the local OpenAI-compatible API used by Open WebUI.
  - The documented primary endpoint remains `http://127.0.0.1:8000/v1`.

- **Failure behavior**:
  - Missing FastAPI or Uvicorn remains a blocking error.
  - Existing runtime import or startup failures continue to surface as actionable errors.

## UI Migration Contract

- **Command**:

```bash
local-model ui [--api-base-url http://127.0.0.1:8000]
```

- **Success behavior**:
  - The command no longer launches any native macOS application.
  - It prints migration guidance telling the operator to:
    - start `local-model serve`
    - connect Open WebUI to `http://127.0.0.1:8000/v1`
    - verify service availability with `curl http://127.0.0.1:8000/health`
    - verify model discovery with `curl http://127.0.0.1:8000/v1/models` or `local-model list-models --json`
  - The guidance includes a note for Dockerized Open WebUI users to prefer `host.docker.internal`.
  - When `--api-base-url` is supplied, the command normalizes the Open WebUI URL to the `/v1` prefix and uses that value in its recovery hints.

- **Failure behavior**:
  - The command exits non-zero after printing the migration message so automation and users can distinguish the retired workflow from a functioning UI launch.
  - The command does not attempt to probe the endpoint itself; instead it prints the verification commands an operator should run when the service is down, the endpoint is wrong, or no models are visible.

## Discovery and Run Contract

- **Commands**:

```bash
local-model list-models [--json]
local-model run <alias> ...
local-model chat <alias> ...
```

- **Contract**:
  - No behavioral changes are required for this feature.
  - Existing model registration, discovery, runtime selection, and generation flows remain the source of truth behind the Open WebUI workflow.
