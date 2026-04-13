# Data Model: Add streaming chat completions with reasoning output

## Entity: Chat Completion Session

- **Purpose**: Represents one request to `POST /v1/chat/completions`, including runtime selection, streaming mode, and final completion state.
- **Primary Fields**:
  - `request_id`: opaque identifier returned to the client
  - `model_alias`: registered model selected for the session
  - `stream`: whether the response is emitted incrementally
  - `requested_runtime`: runtime requested by the client or preset
  - `active_runtime`: runtime that actually served the request
  - `preset_name`: preset used to derive runtime defaults and generation settings
  - `status`: `pending`, `streaming`, `completed`, or `failed`
  - `finish_reason`: terminal outcome such as `stop`, `length`, or runtime interruption
  - `fallback_reason`: optional explanation when runtime fallback occurs
- **Validation Rules**:
  - `active_runtime` must be known before the first streamed delta is emitted.
  - `status = streaming` is valid only when `stream = true`.
  - A successful streamed session must end with a terminal completion signal; an interrupted stream must be distinguishable by the absence of that signal.
  - Non-streamed sessions must continue to return the established single-response contract.

## Entity: Stream Delta

- **Purpose**: Represents one ordered unit of output sent to the client during a streamed chat-completion session.
- **Primary Fields**:
  - `sequence`: monotonically increasing position within the stream
  - `role`: assistant role marker, typically present in the first delta
  - `content_delta`: final-answer text emitted in this fragment
  - `reasoning_delta`: reasoning text emitted in this fragment, when present
  - `finish_reason`: terminal marker on the last JSON chunk before `[DONE]`
  - `created_at`: session timestamp reused across related deltas
- **Validation Rules**:
  - Deltas must preserve generation order.
  - `content_delta` and `reasoning_delta` may both be empty only for the terminal chunk.
  - Only the last JSON chunk may carry a non-null `finish_reason`.
  - A successful stream must be followed by the transport sentinel `data: [DONE]`.

## Entity: Reasoning Transcript

- **Purpose**: Tracks model-emitted reasoning text separately from the final assistant answer so clients can consume or ignore it without reparsing the answer content.
- **Primary Fields**:
  - `format`: declared reasoning format, such as `think_tags` or `none`
  - `raw_buffer`: verbatim reasoning-oriented text received from the model
  - `normalized_buffer`: parser-stable reasoning text after partial-tag normalization
  - `answer_buffer`: clean final-answer text after reasoning text is separated
  - `open_segment`: whether the parser is currently inside a reasoning segment
- **Validation Rules**:
  - `normalized_buffer` must contain only model-emitted reasoning content; parser-added markers may normalize structure but must not invent reasoning text.
  - `answer_buffer` must exclude reasoning text.
  - Partial tag boundaries that cross token or chunk boundaries must still produce a valid reconstructed reasoning transcript.
  - If the model emits no reasoning content, `format` must resolve to `none` and the reasoning buffers remain empty.

## Entity: Runtime Capability Profile

- **Purpose**: Declares whether a preset or manifest can satisfy streaming and reasoning-aware chat behavior.
- **Primary Fields**:
  - `default_preset`
  - `supported_runtimes`
  - `supports_streaming`
  - `reasoning_format`
  - `reasoning_enabled_by_default`
  - `fallback_allowed`
- **Validation Rules**:
  - `supports_streaming = true` requires a runtime path that can emit true token deltas.
  - `reasoning_format != none` must not be claimed for a model or preset that never emits reasoning text.
  - Capability metadata must not require committed changes under `models/cache/`.
  - Runtime fallback must not silently downgrade a session from reasoning-capable to non-reasoning without surfacing that change in diagnostics or session metadata.

## Relationships

- A **Chat Completion Session** selects exactly one **Runtime Capability Profile** before generation begins.
- A streamed **Chat Completion Session** emits one or more **Stream Deltas** and may update one **Reasoning Transcript** over time.
- A completed **Reasoning Transcript** contributes optional reasoning fields to the final session payload, while the session’s clean answer content is built from the transcript’s `answer_buffer`.
- Capability metadata in manifests or presets determines whether a session may legally enter streamed or reasoning-aware modes on the chosen runtime.
