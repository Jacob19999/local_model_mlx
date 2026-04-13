# API Contract: Local Service for Open WebUI

## Health Endpoint

- **Route**: `GET /health`
- **Contract**:
  - Returns service availability and the count of registered models.
  - No new fields are required for the Open WebUI migration.
  - Operators can verify service reachability with `curl http://127.0.0.1:8000/health`.

## Model Discovery Endpoint

- **Route**: `GET /v1/models`
- **Contract**:
  - Returns the standard model-card list for manifests where `api_visible` is true.
  - Each card continues to expose:
    - `id`
    - `object`
    - `owned_by`
    - `runtime`
    - `turboquant_compatible`
  - This endpoint remains the discovery source for the supported Open WebUI workflow.
  - Operators can verify model visibility with `curl http://127.0.0.1:8000/v1/models`.

## Chat Completions Endpoint

- **Route**: `POST /v1/chat/completions`
- **Request contract**:
  - `model`: registered alias
  - `messages`: non-empty chat message list
  - optional `runtime`
  - optional `preset`
  - optional `fallback_allowed`
  - optional `max_tokens`
  - optional `temperature`

- **Success contract**:
  - Exit status `200`
  - Response includes:
    - `id`
    - `object`
    - `created`
    - `model`
    - `runtime`
    - `choices[0].message.content`

- **Failure contract**:
  - Unknown aliases return `404`
  - Runtime or generation preflight failures return `400`
  - No new API auth requirements are introduced by this feature

## Verification Commands

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/models
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"demo-openwebui","messages":[{"role":"user","content":"Hello"}]}'
```

- If `/health` fails, `local-model serve` is not reachable at the configured host or port.
- If `/v1/models` returns an empty list, the operator should confirm that at least one manifest is registered and API-visible.

## Out-of-Scope Note

- The Open WebUI migration does not expand the local service to cover embeddings,
  image generation, voice, or other optional provider features.
