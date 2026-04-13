# API Contract: Streaming Chat Completions with Reasoning Output

## Health Endpoint

- **Route**: `GET /health`
- **Contract**:
  - Returns service availability and the count of registered models.
  - This feature does not require new health fields.

## Model Discovery Endpoint

- **Route**: `GET /v1/models`
- **Contract**:
  - Continues to return model cards for manifests where `api_visible` is true.
  - Existing fields remain:
    - `id`
    - `object`
    - `owned_by`
    - `runtime`
    - `turboquant_compatible`
  - This feature may add backward-compatible capability hints such as streaming or reasoning support, but it does not introduce a second model-discovery endpoint.

## Chat Completions Endpoint

- **Route**: `POST /v1/chat/completions`

### Request contract

- Required fields:
  - `model`
  - `messages`
- Existing optional fields remain:
  - `runtime`
  - `preset`
  - `fallback_allowed`
  - `max_tokens`
  - `temperature`
- New optional field:
  - `stream`: boolean; when `true`, the response uses the streamed contract below

### Non-stream success contract

- **Status**: `200`
- **Body**:
  - `id`
  - `object = "chat.completion"`
  - `created`
  - `model`
  - `runtime`
  - `choices[0].message.role = "assistant"`
  - `choices[0].message.content`: clean final assistant answer
  - optional `choices[0].message.reasoning_content`: normalized reasoning text when the selected model emits it
  - `choices[0].finish_reason`
- **Compatibility rule**:
  - Requests that omit `stream` or set it to `false` continue to receive a single JSON response.

### Stream success contract

- **Status**: `200`
- **Content-Type**: `text/event-stream`
- **Transport**:
  - Emits `data: {json}` lines whose payload object is `chat.completion.chunk`
  - Ends successful streams with `data: [DONE]`
- **Chunk body shape**:
  - `id`
  - `object = "chat.completion.chunk"`
  - `created`
  - `model`
  - `choices[0].index = 0`
  - `choices[0].delta.role`: present on the initial assistant chunk
  - optional `choices[0].delta.content`: answer text fragment
  - optional `choices[0].delta.reasoning_content`: reasoning text fragment
  - `choices[0].finish_reason`: `null` until the terminal JSON chunk, then `stop` or `length`
- **Ordering rules**:
  - Chunks must preserve generation order.
  - `delta.reasoning_content` may appear before, after, or interleaved with `delta.content` according to the parser state, but the final reconstructed answer content must exclude reasoning text.
  - The last JSON chunk carries the terminal `finish_reason`, and a successful stream is then followed by `data: [DONE]`.

### Failure contract

- Unknown model aliases return `404` before streaming begins.
- Preflight, runtime-selection, or generation setup failures return `400` before streaming begins.
- If a failure occurs after partial streamed output has already been emitted, the connection closes without the final `[DONE]` sentinel; clients must treat the missing sentinel as an interrupted stream.
- The API must not fabricate `reasoning_content` fields for models that do not emit reasoning text.

## Out-of-Scope Note

- This feature does not add embeddings, tools, images, audio, multiple choices, or usage-accounting parity beyond what is required to make streamed chat completions consumable.
