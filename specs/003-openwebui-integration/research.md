# Research: Replace macOS UI with Open WebUI

## Decision 1: Use documentation-driven Open WebUI onboarding instead of bundling a new in-repo UI

- **Decision**: Treat Open WebUI as an external, operator-installed UI and document the supported connection flow to the existing local API instead of creating or vendoring a new UI application inside this repository.
- **Rationale**: The feature request is to stop investing in the native macOS shell while continuing to use the API that already exists. Open WebUI’s official guidance is protocol-oriented and expects an OpenAI-compatible backend. That matches the current service direction more closely than maintaining a second in-repo UI codebase. Documentation is lower-risk than packaging, forking, or embedding another application lifecycle inside this repo.
- **Alternatives considered**:
  - Build a new in-repo browser UI: rejected because it recreates the same maintenance burden the feature is trying to remove.
  - Vendor Open WebUI into the repository: rejected because it would add an unrelated application stack and deployment surface.
  - Keep the SwiftUI shell as a secondary option: rejected because it preserves the split UI investment the feature is intended to end.

## Decision 2: Keep `local-model serve` and the current API contract unchanged for the first migration

- **Decision**: Preserve `local-model serve`, `GET /health`, `GET /v1/models`, and `POST /v1/chat/completions` as the first migration target for Open WebUI.
- **Rationale**: The current repo already has a local OpenAI-compatible service, and Open WebUI officially supports OpenAI-compatible providers using the standard chat-completions protocol. Keeping the existing service contract avoids unnecessary runtime churn and lets this feature focus on operator experience, deprecation, and documentation.
- **Alternatives considered**:
  - Replace the local service with a different backend such as `llama.cpp`: rejected because it would change model format and runtime assumptions far beyond the requested UI migration.
  - Expand the API to cover embeddings, images, or other provider features as part of this feature: rejected because the spec only requires basic model discovery and chat onboarding.

## Decision 3: Remove native UI assets but keep CLI and script migration shims

- **Decision**: Delete `apps/macos-ui/`, keep `local-model ui` as a non-launching migration shim, and repurpose `scripts/launch_ui.sh` as a helper that prints the supported Open WebUI workflow and endpoint details.
- **Rationale**: Fully deleting the command would make the old workflow fail with a generic parser error and give operators no path forward. A migration shim keeps the CLI as the public control plane, helps existing users recover quickly, and still satisfies the requirement to stop maintaining the native UI surface because the command no longer launches that shell.
- **Alternatives considered**:
  - Remove `local-model ui` entirely: rejected because it produces a poorer migration experience and weakens the CLI’s role as the public operator contract.
  - Keep `local-model ui` or `scripts/launch_ui.sh` launching a new bundled web UI: rejected because it would reintroduce an in-repo UI surface.

## Decision 4: Prefer a native Open WebUI connection flow that uses `http://127.0.0.1:8000/v1`

- **Decision**: Make the first-party documented endpoint `http://127.0.0.1:8000/v1` for operators running Open WebUI on the same host, and document `host.docker.internal` only as a containerized fallback note.
- **Rationale**: The requested endpoint is `http://127.0.0.1:8000/v1`, which works directly when Open WebUI runs natively on the same machine. Open WebUI’s own docs note that Docker users should replace `localhost` with `host.docker.internal`, so that remains a secondary note rather than the primary path.
- **Alternatives considered**:
  - Make Docker the primary documented path: rejected because the requested endpoint would no longer be correct inside the container.
  - Require operators to preseed Open WebUI config through repository-managed environment variables: rejected because Open WebUI stores connection settings persistently and the admin-panel flow is clearer and more reliable.

## Decision 5: Scope the migration to basic chat and model discovery, not advanced Open WebUI features

- **Decision**: Limit this feature to the parts of Open WebUI that depend on model discovery and chat completions, and explicitly leave embeddings, RAG, voice, image generation, and agent/tool workflows out of scope.
- **Rationale**: Open WebUI can connect to many OpenAI-compatible providers, but advanced features often depend on additional endpoints or provider-specific settings. The local service currently exposes `/v1/models` and `/v1/chat/completions`, which is enough for basic chat onboarding. The plan should not overpromise compatibility that the backend does not yet provide.
- **Alternatives considered**:
  - Claim full Open WebUI feature parity: rejected because the existing backend contract does not support those capabilities today.
  - Delay the UI migration until every optional Open WebUI feature is supported: rejected because it would block the requested simplification on unrelated backend work.

## Sources Consulted

- Open WebUI Quick Start home page: <https://docs.openwebui.com/>
- Open WebUI OpenAI-compatible provider guide: <https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/>
- Open WebUI vLLM connection guide: <https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-vllm/>
- Open WebUI environment configuration reference: <https://docs.openwebui.com/reference/env-configuration/>
