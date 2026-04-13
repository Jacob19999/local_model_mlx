# API Contract: Nemotron 3 Nano 30B A3B Discovery and Inference

## Health Endpoint

- **Route**: `GET /health`
- **Contract**:
  - Returns service availability plus the count of registered models
  - Nemotron support does not add new fields

## Model Discovery Endpoint

- **Route**: `GET /v1/models`
- **Contract**:
  - Returns the standard model-card list for manifests where `api_visible` is true
  - After a successful install, the response includes:
    - `id`: installed alias, for example `nemotron-3-nano-30b-a3b`
    - `object`: `model`
    - `owned_by`: `local-model`
    - `runtime`: manifest default runtime
    - `turboquant_compatible`: manifest runtime capability flag
  - Invalid or incomplete manifests are excluded from discovery.

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
    - `runtime`: manifest summary for the resolved model
    - `choices[0].message.content`

- **Failure contract**:
  - Unknown Nemotron alias returns `404`
  - Runtime or generation preflight failures return `400`
  - Failures must occur before any partial success payload is returned
  - Failed installs never appear in `/v1/models`
