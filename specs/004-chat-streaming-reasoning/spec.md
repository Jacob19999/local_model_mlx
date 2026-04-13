# Feature Specification: Add streaming chat completions with reasoning output

**Feature Branch**: `004-chat-streaming-reasoning`  
**Created**: 2026-04-12  
**Status**: Draft  
**Input**: User description: "OpenAI-style streaming for /v1/chat/completions with stream: true incremental token generation in the runner layer reasoning output support, ideally with <think>...</think> tags or another parser-compatible format optional model/settings changes if your chosen model does not actually produce reasoning text"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive chat output incrementally (Priority: P1)

As an API client using the local chat endpoint, I can request streamed chat completions so I see assistant output arrive progressively instead of waiting for the full answer to finish.

**Why this priority**: Streaming is the core user-visible capability in scope and is required for compatibility with clients that expect incremental chat updates.

**Independent Test**: Can be fully tested by sending a chat completion request with `stream` enabled, observing multiple ordered partial updates before completion, and confirming that the same request still returns a single completed response when streaming is disabled.

**Acceptance Scenarios**:

1. **Given** a registered model that can produce a multi-token reply, **When** the client sends a chat completion request with `stream` enabled, **Then** the endpoint keeps the response open and emits ordered partial assistant updates until the reply is complete.
2. **Given** the same prompt and model, **When** the client sends the request without `stream` or with `stream` disabled, **Then** the endpoint returns the existing single-response chat completion shape instead of a streamed response.

---

### User Story 2 - Consume reasoning safely (Priority: P2)

As a reasoning-aware client, I can receive model reasoning in a parser-compatible form so I can display, strip, or analyze it without corrupting the final assistant answer.

**Why this priority**: Reasoning output is a requested compatibility feature and must be exposed predictably for clients that differentiate hidden thinking from the final answer.

**Independent Test**: Can be fully tested by using a reasoning-capable model or settings path, confirming that reasoning output is exposed in a parseable format during generation, and verifying that the final assistant answer remains intact and distinguishable from reasoning text.

**Acceptance Scenarios**:

1. **Given** a reasoning-capable model or settings path, **When** the client requests a chat completion, **Then** any emitted reasoning content is surfaced in a parser-compatible format such as tagged reasoning text or an equivalent clearly separable representation.
2. **Given** a model or settings path that does not emit reasoning, **When** the client requests a chat completion, **Then** the system returns the assistant answer without fabricating reasoning content.

---

### User Story 3 - Use a supported reasoning-capable configuration (Priority: P3)

As an operator exposing local models through the API, I can use a supported model or settings configuration that provides streaming and reasoning behavior without breaking existing chat clients.

**Why this priority**: The feature only delivers value if the repository offers at least one supported path that actually emits the requested reasoning behavior.

**Independent Test**: Can be fully tested by starting the local API with the supported configuration, verifying that streamed chat works end to end, and confirming that operators can identify when a selected model lacks reasoning support and switch to the supported path.

**Acceptance Scenarios**:

1. **Given** the current default model path does not emit reasoning text, **When** the operator uses the supported alternative model or settings path for this feature, **Then** streamed chat completions expose reasoning in the documented parser-compatible format.
2. **Given** the operator selects a model that supports standard chat but not reasoning output, **When** the client sends a reasoning-aware request, **Then** the response remains a valid chat completion and the absence of reasoning output is not presented as a failure of the assistant answer.

### Edge Cases

- What happens when a client disconnects after partial streamed output has already been sent?
- What happens when generation fails after one or more partial updates have already been delivered?
- How is reasoning handled when the model emits tagged thinking text split across multiple incremental updates?
- What happens when the selected model can generate chat text but cannot stream incrementally through the active runtime path?
- How does the endpoint behave when `stream` is enabled for a prompt that completes immediately with little or no generated text?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a `stream` toggle on the chat completion request and treat disabled or omitted streaming as the current single-response behavior.
- **FR-002**: The system MUST provide an OpenAI-style streamed response mode for `POST /v1/chat/completions` when `stream` is enabled.
- **FR-003**: In streamed mode, the system MUST emit assistant output incrementally in the order it is generated so clients can render partial replies before completion.
- **FR-004**: The generation path behind streamed chat MUST produce output incrementally from the runner layer rather than buffering the entire assistant reply before sending the first streamed update.
- **FR-005**: The streamed response MUST include a clear terminal signal so clients can distinguish a completed reply from an interrupted or failed one.
- **FR-006**: The system MUST preserve compatibility for existing clients that use `/v1/chat/completions` without streaming by keeping the current non-streaming response contract intact.
- **FR-007**: When the active model or settings path emits reasoning content, the system MUST expose that reasoning in a parser-compatible format that keeps it distinguishable from the final assistant answer.
- **FR-008**: The parser-compatible reasoning format MUST remain valid even when reasoning content arrives across multiple incremental updates.
- **FR-009**: The system MUST NOT invent, infer, or backfill reasoning text when the selected model or settings path does not actually emit reasoning output.
- **FR-010**: The system MUST preserve the final assistant answer as a clean consumable response whether or not reasoning content is present.
- **FR-011**: If the current default model path cannot produce reasoning output, the repository MUST provide at least one supported model or settings path that does, or clearly scope reasoning support to the supported configurations only.
- **FR-012**: The feature MUST keep model selection semantics consistent with the existing `/v1/models` and `/v1/chat/completions` flow so streaming does not require a new discovery surface.
- **FR-013**: Error handling for streamed requests MUST remain user-diagnosable when generation fails before completion or when the runtime cannot satisfy incremental streaming expectations.

### Runtime, CLI & Observability Requirements

- **RCO-001**: The affected public surface is `local-model serve` and its `POST /v1/chat/completions` endpoint; no separate interactive command is required for this feature.
- **RCO-002**: The runtime paths in scope are the existing text-generation runners exposed behind the local API; if an active runtime cannot support true incremental generation or reasoning output, the system MUST fail or fall back in a way that is explicit to the operator rather than silently simulating streamed output.
- **RCO-003**: This feature MUST NOT require committed model artifacts under `models/cache/`; any required support changes are limited to committed settings or model metadata under existing tracked configuration locations.
- **RCO-004**: User-visible diagnostics for this feature MUST make it possible to determine which model and runtime served the request, whether streaming mode was active, and whether reasoning content was emitted or unavailable.

### Key Entities *(include if feature involves data)*

- **Streamed Chat Session**: A single chat completion request whose reply is delivered as ordered partial updates followed by a terminal completion signal.
- **Chat Delta**: A partial unit of assistant output that lets a client progressively reconstruct the reply during a streamed session.
- **Reasoning Segment**: Model-emitted thinking content that is intentionally separable from the final assistant answer and safe for parser-driven handling.
- **Supported Reasoning Configuration**: A model alias, preset, or settings path that the repository treats as a valid way to expose reasoning output through the local API.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For representative prompts that produce multi-token replies, clients using streamed chat receive visible assistant output before the final completion signal and can reconstruct the reply from the ordered partial updates.
- **SC-002**: 100% of existing chat completion requests that omit `stream` or set it to disabled continue to succeed with the established single-response contract.
- **SC-003**: In a supported reasoning-capable configuration, reasoning-aware clients can distinguish reasoning content from the final assistant answer in both streamed and completed responses.
- **SC-004**: Operators can identify, without code inspection, whether a selected model path supports reasoning output and whether a failed streamed request was caused by runtime limitations or by generation failure.

## Assumptions

- The initial scope remains limited to standard text chat completions and does not add tool invocation, audio, image generation, or multi-choice streaming behavior.
- A parser-compatible reasoning representation such as `<think>...</think>` tags or an equivalent separable format is acceptable so long as clients can reliably distinguish reasoning from the final answer.
- If the repository’s current default model path does not emit reasoning text, adjusting supported model metadata or settings is an acceptable way to provide at least one supported reasoning-capable path.
- Usage accounting, advanced stream options, and other broader OpenAI compatibility features remain out of scope unless they are required to make the new streaming behavior consumable.
