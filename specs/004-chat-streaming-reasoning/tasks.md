# Tasks: Add streaming chat completions with reasoning output

**Input**: Design documents from `/Users/Apple/Documents/local_model_mlx/specs/004-chat-streaming-reasoning/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/local-model-api.md`, `contracts/local-model-cli.md`, `quickstart.md`

**Tests & Validation**: The plan explicitly requires targeted `pytest` unit, contract, and integration coverage plus manual `curl -N` smoke validation for streamed chat.

**Organization**: Tasks are grouped by user story so each increment can be implemented and validated with clear scope.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the shared helpers and fixtures needed by the feature work.

- [X] T001 Create SSE chunk serialization helpers in `src/local_model/services/streaming.py`
- [X] T002 [P] Create reasoning parser scaffolding in `src/local_model/services/reasoning_parser.py`
- [X] T003 [P] Add reusable streaming and runner fixtures in `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend the shared runtime and API types that every story depends on.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Extend shared generation dataclasses for stream deltas, reasoning transcripts, and capability metadata in `src/local_model/models.py`
- [X] T005 [P] Add `stream` and reasoning-aware schema models in `src/local_model/api/schemas.py`
- [X] T006 [P] Expand runner interfaces for incremental generation support in `src/local_model/runners/base.py`
- [X] T007 [P] Add capability-aware manifest summaries and runtime diagnostics in `src/local_model/services/diagnostics.py`
- [X] T008 Update runtime selection to enforce explicit streaming eligibility and fallback semantics in `src/local_model/services/runtime_resolver.py`

**Checkpoint**: Shared streaming, reasoning, and capability primitives are ready for story work.

---

## Phase 3: User Story 1 - Receive chat output incrementally (Priority: P1) 🎯 MVP

**Goal**: Deliver real runner-layer incremental chat streaming while preserving the existing non-stream response contract.

**Independent Test**: Send the same `POST /v1/chat/completions` request with and without `stream`; the streamed call must emit multiple ordered chunks before `data: [DONE]`, while the non-streamed call must still return one `chat.completion` payload.

### Validation for User Story 1

- [X] T009 [P] [US1] Add contract coverage for streamed and non-streamed chat completions in `tests/contract/test_api_openwebui_compat.py`
- [X] T010 [P] [US1] Add end-to-end streamed API coverage with ordered deltas and `[DONE]` termination in `tests/integration/test_api_streaming_chat.py`
- [X] T011 [P] [US1] Add runner unit coverage for incremental MLX token emission in `tests/unit/test_mlx_runner.py`

### Implementation for User Story 1

- [X] T012 [US1] Implement stock MLX incremental generation with `mlx_lm` streaming APIs in `src/local_model/runners/mlx_runner.py`
- [X] T013 [US1] Implement shared chat execution helpers that preserve the non-stream path in `src/local_model/cli.py`
- [X] T014 [US1] Implement SSE chat completion responses and terminal chunk emission in `src/local_model/api/server.py`

**Checkpoint**: Streamed chat works end to end and non-stream chat remains backward-compatible.

---

## Phase 4: User Story 2 - Consume reasoning safely (Priority: P2)

**Goal**: Separate model-emitted reasoning from final answer text in both streamed and completed responses.

**Independent Test**: Use a reasoning-capable prompt or fixture and verify `reasoning_content` is surfaced separately from the assistant answer, including when `<think>` boundaries arrive across multiple streamed fragments.

### Validation for User Story 2

- [X] T015 [P] [US2] Add unit coverage for partial reasoning-tag normalization in `tests/unit/test_reasoning_parser.py`
- [X] T016 [P] [US2] Add contract coverage for `reasoning_content` in streamed and completed responses in `tests/contract/test_api_reasoning.py`
- [X] T017 [P] [US2] Add integration coverage for mixed reasoning and answer deltas in `tests/integration/test_api_reasoning_stream.py`

### Implementation for User Story 2

- [X] T018 [US2] Implement incremental reasoning transcript normalization in `src/local_model/services/reasoning_parser.py`
- [X] T019 [US2] Extend generation result models with reasoning buffers and clean final answer fields in `src/local_model/models.py`
- [X] T020 [US2] Propagate reasoning fragments through stock MLX one-shot and streamed generation in `src/local_model/runners/mlx_runner.py`
- [X] T021 [US2] Wire reasoning-aware chunk assembly and final message shaping in `src/local_model/api/server.py`

**Checkpoint**: Reasoning-aware clients can consume separate reasoning output without polluting final assistant content.

---

## Phase 5: User Story 3 - Use a supported reasoning-capable configuration (Priority: P3)

**Goal**: Expose at least one supported configuration that advertises streaming and reasoning support and makes runtime behavior operator-visible.

**Independent Test**: Start the service with the supported configuration, verify `/v1/models` and diagnostics show the capability hints, and confirm unsupported streamed runtime requests fail or fall back explicitly before generation starts.

### Validation for User Story 3

- [X] T022 [P] [US3] Add unit coverage for capability-driven runtime resolution and unsupported streamed runtime failures in `tests/unit/test_runtime_resolver_nemotron.py`
- [X] T023 [P] [US3] Add integration coverage for capability discovery and operator-visible runtime diagnostics in `tests/integration/test_nemotron_discovery_run.py`
- [X] T024 [P] [US3] Add contract coverage for model capability hints in `tests/contract/test_api_nemotron.py`

### Implementation for User Story 3

- [X] T025 [US3] Add streaming and reasoning capability metadata to the supported manifest in `models/manifests/nemotron-3-nano-30b-a3b.yaml`
- [X] T026 [US3] Add a reasoning-capable API preset and fallback policy updates in `configs/presets.yaml`
- [X] T027 [US3] Update supported-model defaults and capability documentation in `configs/models.yaml`
- [X] T028 [US3] Surface capability hints in `/v1/models` and operator diagnostics in `src/local_model/api/server.py`
- [X] T029 [US3] Document supported reasoning configurations and failure modes in `README.md`

**Checkpoint**: Operators can identify supported reasoning-capable paths and diagnose unsupported runtime behavior without reading code.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation and validation that cut across all stories.

- [X] T030 [P] Refresh operator smoke steps for streaming, reasoning, and fallback validation in `specs/004-chat-streaming-reasoning/quickstart.md`
- [X] T031 Run targeted `pytest` coverage for streaming and reasoning changes in `tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and can start immediately.
- Foundational (Phase 2) depends on Phase 1 and blocks all story work.
- User Story 1 (Phase 3) depends on Phase 2 and is the MVP.
- User Story 2 (Phase 4) depends on Phase 2 and the streaming transport delivered in Phase 3.
- User Story 3 (Phase 5) depends on Phase 2; metadata tasks can begin early, but final validation depends on the reasoning-aware behavior from Phase 4.
- Polish (Phase 6) depends on the stories you intend to ship.

### User Story Dependencies

- User Story 1 (P1) has no story-level dependencies after the foundational phase.
- User Story 2 (P2) builds on User Story 1 because reasoning output must travel through the streamed and non-streamed chat paths created there.
- User Story 3 (P3) can start its manifest and preset work after the foundational phase, but its full acceptance depends on User Story 2 exposing real reasoning output.

### Within Each User Story

- Write validation coverage before or alongside the implementation tasks it exercises.
- Update runner and transport layers before final API wiring.
- Finish story-specific diagnostics and docs before declaring the story complete.

### Parallel Opportunities

- `T002` and `T003` can run in parallel once `T001` starts the shared setup work.
- `T005`, `T006`, and `T007` can run in parallel after `T004`.
- `T009`, `T010`, and `T011` can run in parallel for User Story 1.
- `T015`, `T016`, and `T017` can run in parallel for User Story 2.
- `T022`, `T023`, and `T024` can run in parallel for User Story 3.
- `T025`, `T026`, and `T027` can run in parallel before `T028` ties capability metadata into the API surface.

---

## Parallel Example: User Story 1

```bash
Task: "Add contract coverage for streamed and non-streamed chat completions in tests/contract/test_api_openwebui_compat.py"
Task: "Add end-to-end streamed API coverage with ordered deltas and [DONE] termination in tests/integration/test_api_streaming_chat.py"
Task: "Add runner unit coverage for incremental MLX token emission in tests/unit/test_mlx_runner.py"
```

```bash
Task: "Implement stock MLX incremental generation with mlx_lm streaming APIs in src/local_model/runners/mlx_runner.py"
Task: "Implement shared chat execution helpers that preserve the non-stream path in src/local_model/cli.py"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add unit coverage for partial reasoning-tag normalization in tests/unit/test_reasoning_parser.py"
Task: "Add contract coverage for reasoning_content in streamed and completed responses in tests/contract/test_api_reasoning.py"
Task: "Add integration coverage for mixed reasoning and answer deltas in tests/integration/test_api_reasoning_stream.py"
```

```bash
Task: "Implement incremental reasoning transcript normalization in src/local_model/services/reasoning_parser.py"
Task: "Extend generation result models with reasoning buffers and clean final answer fields in src/local_model/models.py"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add unit coverage for capability-driven runtime resolution and unsupported streamed runtime failures in tests/unit/test_runtime_resolver_nemotron.py"
Task: "Add integration coverage for capability discovery and operator-visible runtime diagnostics in tests/integration/test_nemotron_discovery_run.py"
Task: "Add contract coverage for model capability hints in tests/contract/test_api_nemotron.py"
```

```bash
Task: "Add streaming and reasoning capability metadata to the supported manifest in models/manifests/nemotron-3-nano-30b-a3b.yaml"
Task: "Add a reasoning-capable API preset and fallback policy updates in configs/presets.yaml"
Task: "Update supported-model defaults and capability documentation in configs/models.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate streamed and non-streamed chat behavior before expanding scope.

### Incremental Delivery

1. Deliver Setup + Foundational so the shared streaming and reasoning primitives are stable.
2. Ship User Story 1 as the MVP for OpenAI-style streaming compatibility.
3. Add User Story 2 to expose reasoning safely without changing the clean-answer contract.
4. Add User Story 3 to publish a supported reasoning-capable configuration and operator guidance.
5. Finish with quickstart refresh and targeted regression runs.

### Parallel Team Strategy

1. One engineer handles shared runtime and API primitives in Phases 1-2.
2. Once Phase 2 is complete, one engineer can take User Story 1 while another prepares User Story 3 metadata and validation scaffolding.
3. User Story 2 should begin after the User Story 1 transport is stable because it plugs reasoning parsing into that path.
