---

description: "Task list for implementing MLX-LM TurboQuant KV Cache"
---

# Tasks: MLX-LM TurboQuant KV Cache

**Input**: Design documents from `/specs/001-mlx-lm-turboquant-kvcache/`
**Prerequisites**: `plan.md`, `spec.md`, `PLAN.md`, `.specify/memory/constitution.md`

**Tests & Validation**: Use targeted `pytest` unit, integration, and contract coverage for each story. Capture the end-to-end CLI, API, and UI smoke workflow in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`.

**Organization**: Tasks are grouped by user story so each increment can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold the greenfield repository for the Python runtime, CLI, config storage, and local app shell.

- [ ] T001 Initialize package metadata and runtime dependencies in `pyproject.toml`
- [ ] T002 Create the base Python package and CLI entrypoint in `src/local_model/__init__.py`, `src/local_model/__main__.py`, and `src/local_model/cli.py`
- [ ] T003 [P] Add cache-safe ignore rules and local artifact defaults in `.gitignore`
- [ ] T004 [P] Create committed config and model metadata directories in `configs/.gitkeep`, `models/manifests/.gitkeep`, and `models/cache/.gitignore`
- [ ] T005 [P] Add bootstrap and local launch helper scripts in `scripts/bootstrap.sh` and `scripts/launch_ui.sh`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared runtime abstractions, registry, process control, and diagnostics that every story depends on.

**⚠️ CRITICAL**: Complete this phase before starting user story work.

- [ ] T006 Define the shared runtime adapter protocol and session metadata in `src/local_model/runners/base.py` and `src/local_model/models.py`
- [ ] T007 [P] Implement config loading and manifest registry helpers in `src/local_model/config.py` and `src/local_model/registry.py`
- [ ] T008 [P] Implement shared process and stream orchestration in `src/local_model/services/process_manager.py`
- [ ] T009 [P] Implement runtime resolution and active-path selection in `src/local_model/services/runtime_resolver.py`
- [ ] T010 Implement structured diagnostics and environment checks in `src/local_model/services/diagnostics.py` and `src/local_model/doctor.py`

**Checkpoint**: The runtime foundation is ready; story work can proceed in priority order.

---

## Phase 3: User Story 1 - Launch supported models from the CLI (Priority: P1) 🎯 MVP

**Goal**: Let operators select a supported model alias from one stable `local-model` command shape.

**Independent Test**: Launch two configured aliases through the same CLI flow and confirm the selected model changes while the command family stays the same.

### Validation for User Story 1

- [ ] T011 [P] [US1] Add CLI integration coverage for alias-based launch flows in `tests/integration/test_cli_model_selection.py`
- [ ] T012 [P] [US1] Add unit coverage for model and preset loading in `tests/unit/test_registry_and_presets.py`

### Implementation for User Story 1

- [ ] T013 [P] [US1] Define supported model aliases and stock runtime presets in `configs/models.yaml` and `configs/presets.yaml`
- [ ] T014 [P] [US1] Add committed stock model manifest fields in `models/manifests/sample-stock-text.yaml`
- [ ] T015 [US1] Implement the stock MLX runner and session banner output in `src/local_model/runners/mlx_runner.py`
- [ ] T016 [US1] Implement `local-model run` and `local-model chat` model-selection flows in `src/local_model/cli.py`

**Checkpoint**: User Story 1 is complete when the CLI can switch supported models without changing command families.

---

## Phase 4: User Story 2 - Enable TurboQuant runs (Priority: P2)

**Goal**: Allow the same text-generation flow to run through an optional TurboQuant KV cache path for compatible models.

**Independent Test**: Launch a compatible model with TurboQuant enabled and confirm generation succeeds while the runtime surface reports the TurboQuant path before tokens stream.

### Validation for User Story 2

- [ ] T017 [P] [US2] Add integration coverage for TurboQuant runtime selection in `tests/integration/test_turboquant_runtime.py`
- [ ] T018 [P] [US2] Add unit coverage for TurboQuant compatibility and adapter behavior in `tests/unit/test_turbo_runner.py`

### Implementation for User Story 2

- [ ] T019 [P] [US2] Extend runtime presets and manifest capability flags for TurboQuant in `configs/presets.yaml` and `models/manifests/sample-stock-text.yaml`
- [ ] T020 [P] [US2] Implement the TurboQuant adapter and compatibility checks in `src/local_model/runners/turbo_runner.py`
- [ ] T021 [US2] Route TurboQuant selection through the shared CLI runtime path in `src/local_model/cli.py`
- [ ] T022 [US2] Emit active TurboQuant-path notices before generation in `src/local_model/services/diagnostics.py`

**Checkpoint**: User Story 2 is complete when TurboQuant-enabled generation uses the same operator flow as stock MLX with explicit runtime reporting.

---

## Phase 5: User Story 3 - Preserve safe fallback behavior (Priority: P3)

**Goal**: Keep sessions usable and diagnosable when the TurboQuant path is unavailable or unsupported.

**Independent Test**: Request TurboQuant in an unsupported environment and confirm the system either falls back to stock MLX with a clear notice or halts before generation with an actionable diagnostic.

### Validation for User Story 3

- [ ] T023 [P] [US3] Add integration coverage for degraded-mode fallback behavior in `tests/integration/test_runtime_fallback.py`
- [ ] T024 [P] [US3] Add unit coverage for TurboQuant doctor and compatibility checks in `tests/unit/test_doctor.py`

### Implementation for User Story 3

- [ ] T025 [P] [US3] Encode fallback policy and unsupported-model rules in `configs/presets.yaml` and `models/manifests/sample-stock-text.yaml`
- [ ] T026 [US3] Implement preflight validation and stock-path fallback decisions in `src/local_model/services/runtime_resolver.py`
- [ ] T027 [US3] Implement recovery messaging and non-silent failure output in `src/local_model/doctor.py` and `src/local_model/cli.py`

**Checkpoint**: User Story 3 is complete when every failed TurboQuant attempt ends in an explicit fallback or a clear pre-generation stop.

---

## Phase 6: User Story 4 - Access the runtime from UI and third-party clients (Priority: P4)

**Goal**: Expose the same local runtime through a modern MLX-style macOS shell and an OpenAI-compatible local API.

**Independent Test**: Start the local UI and send one OpenAI-compatible request to the local API, then confirm both surfaces use the same model registry and runtime reporting.

### Validation for User Story 4

- [ ] T028 [P] [US4] Add OpenAI-compatible contract coverage for model listing and chat completions in `tests/contract/test_openai_api.py`
- [ ] T029 [P] [US4] Add integration coverage for launching the macOS shell through the shared runtime flow in `tests/integration/test_ui_launcher.py`

### Implementation for User Story 4

- [ ] T030 [P] [US4] Implement the local OpenAI-compatible service and request schemas in `src/local_model/api/server.py` and `src/local_model/api/schemas.py`
- [ ] T031 [P] [US4] Scaffold the macOS shell that launches shared runtime jobs in `apps/macos-ui/Package.swift` and `apps/macos-ui/Sources/LocalModelApp/App.swift`
- [ ] T032 [US4] Add `local-model serve` and `local-model ui` command wiring in `src/local_model/cli.py` and `scripts/launch_ui.sh`
- [ ] T033 [US4] Surface active model and runtime status in `apps/macos-ui/Sources/LocalModelApp/ViewModels/RuntimeViewModel.swift` and `src/local_model/api/server.py`

**Checkpoint**: User Story 4 is complete when UI and API clients share one runtime contract, model registry, and runtime-path status model.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Finish operator documentation, smoke validation, and cross-story cleanup.

- [ ] T034 [P] Document setup, cache policy, and command examples in `README.md`
- [ ] T035 [P] Document manifest authoring and git-safe cache rules in `models/manifests/README.md`
- [ ] T036 Run the full CLI, TurboQuant, API, and UI smoke workflow and capture it in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`
- [ ] T037 Normalize final operator-facing log and error wording in `src/local_model/cli.py` and `src/local_model/services/diagnostics.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and can start immediately.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- User Story 1 (Phase 3) depends on Foundational and defines the baseline CLI contract.
- User Story 2 (Phase 4) depends on User Story 1 because TurboQuant extends the same launch and chat flow.
- User Story 3 (Phase 5) depends on User Story 2 because fallback behavior is defined around the optional TurboQuant path.
- User Story 4 (Phase 6) depends on User Stories 1 through 3 so the UI and API expose the same model selection, runtime reporting, and fallback behavior.
- Polish (Phase 7) depends on all desired user stories being complete.

### User Story Dependencies

- US1: First deliverable and MVP; no story dependencies after Foundational.
- US2: Builds on the CLI and registry flow from US1.
- US3: Builds on the TurboQuant path from US2.
- US4: Reuses the CLI/runtime contract established in US1-US3 for UI and API clients.

### Within Each User Story

- Write validation coverage before declaring the story complete.
- Update config and manifest data before wiring runtime-specific behavior.
- Implement runtime or service changes before CLI, API, or UI integration.
- Finish operator-facing diagnostics before closing the story.

### Parallel Opportunities

- T003-T005 can run in parallel during Setup.
- T007-T009 can run in parallel during Foundational.
- In US1, T011-T014 can run in parallel because tests, configs, and manifest data touch separate files.
- In US2, T017-T020 can run in parallel before CLI integration in T021.
- In US3, T023-T025 can run in parallel before fallback wiring in T026.
- In US4, T028-T031 can run in parallel before command and UI status integration in T032-T033.
- In Polish, T034-T035 can run in parallel before the final smoke capture in T036.

---

## Parallel Example: User Story 1

```bash
Task: "Add CLI integration coverage for alias-based launch flows in tests/integration/test_cli_model_selection.py"
Task: "Add unit coverage for model and preset loading in tests/unit/test_registry_and_presets.py"
Task: "Define supported model aliases and stock runtime presets in configs/models.yaml and configs/presets.yaml"
Task: "Add committed stock model manifest fields in models/manifests/sample-stock-text.yaml"
```

## Parallel Example: User Story 2

```bash
Task: "Add integration coverage for TurboQuant runtime selection in tests/integration/test_turboquant_runtime.py"
Task: "Add unit coverage for TurboQuant compatibility and adapter behavior in tests/unit/test_turbo_runner.py"
Task: "Implement the TurboQuant adapter and compatibility checks in src/local_model/runners/turbo_runner.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add integration coverage for degraded-mode fallback behavior in tests/integration/test_runtime_fallback.py"
Task: "Add unit coverage for TurboQuant doctor and compatibility checks in tests/unit/test_doctor.py"
Task: "Encode fallback policy and unsupported-model rules in configs/presets.yaml and models/manifests/sample-stock-text.yaml"
```

## Parallel Example: User Story 4

```bash
Task: "Add OpenAI-compatible contract coverage for model listing and chat completions in tests/contract/test_openai_api.py"
Task: "Add integration coverage for launching the macOS shell through the shared runtime flow in tests/integration/test_ui_launcher.py"
Task: "Scaffold the macOS shell that launches shared runtime jobs in apps/macos-ui/Package.swift and apps/macos-ui/Sources/LocalModelApp/App.swift"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the CLI model-selection flow with `tests/integration/test_cli_model_selection.py`.
5. Stop and review before expanding into TurboQuant, fallback, and UI/API work.

### Incremental Delivery

1. Deliver Setup and Foundational so the runtime skeleton is stable.
2. Deliver US1 to establish the baseline CLI contract.
3. Deliver US2 to add the optional TurboQuant path.
4. Deliver US3 to harden fallback and diagnostics.
5. Deliver US4 to expose the same runtime through UI and API clients.
6. Finish with Phase 7 documentation and smoke validation.

### Parallel Team Strategy

1. One engineer completes Setup and Foundational first.
2. After foundation is stable, runtime, validation, and UI/API work can split along the `[P]` tasks in each story.
3. Merge story slices only after their independent tests pass and runtime-path messaging is verified.

---

## Notes

- All tasks use the required checklist format with task IDs, optional parallel markers, required story labels, and concrete file paths.
- `plan.md` in the feature directory is still template-shaped, so task paths are grounded in `PLAN.md`, `spec.md`, and the repository constitution.
- Validation is explicit for every story through tests and a final smoke capture in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`.
