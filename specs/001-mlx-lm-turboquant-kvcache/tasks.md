---

description: "Task list for implementing MLX-LM TurboQuant KV Cache"
---

# Tasks: MLX-LM TurboQuant KV Cache

**Input**: Design documents from `/specs/001-mlx-lm-turboquant-kvcache/`
**Prerequisites**: `plan.md`, `spec.md`, `PLAN.md`, `.specify/memory/constitution.md`

**Tests & Validation**: Benchmarking is out of scope. Capture only the minimal manual smoke workflows needed to prove each user story in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`, plus `doctor` checks for local dependency visibility.

**Organization**: Tasks are grouped by user story so each increment can be implemented and verified independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold the greenfield repository for the Python runtime, CLI surface, cache layout, and plain MLX UI shell.

- [X] T001 Initialize the Python project metadata and runtime dependencies in `pyproject.toml`
- [X] T002 Create the base package and CLI entrypoint in `src/local_model/__init__.py`, `src/local_model/__main__.py`, and `src/local_model/cli.py`
- [X] T003 [P] Add git-safe cache rules and local artifact defaults in `.gitignore` and `models/cache/.gitignore`
- [X] T004 [P] Create committed config and manifest placeholders in `configs/models.yaml`, `configs/presets.yaml`, and `models/manifests/README.md`
- [X] T005 [P] Scaffold helper scripts in `scripts/bootstrap.sh`, `scripts/download_model.sh`, and `scripts/launch_ui.sh`
- [X] T006 [P] Create the TurboQuant fork integration placeholder in `forks/mlx_turboquant/README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared runtime abstractions, registry, install/download services, and diagnostics that every story depends on.

**⚠️ CRITICAL**: Complete this phase before starting user story work.

- [X] T007 Define shared runtime, manifest, and session models in `src/local_model/models.py` and `src/local_model/runners/base.py`
- [X] T008 [P] Implement config loading and manifest discovery in `src/local_model/config.py` and `src/local_model/registry.py`
- [X] T009 [P] Implement shared install and cache placement services in `src/local_model/downloads.py` and `src/local_model/services/install_service.py`
- [X] T010 [P] Implement process orchestration for CLI, API, and UI-launched jobs in `src/local_model/services/process_manager.py`
- [X] T011 [P] Implement runtime selection and operator-facing diagnostics in `src/local_model/services/runtime_resolver.py` and `src/local_model/services/diagnostics.py`
- [X] T012 Add environment visibility and dependency checks in `src/local_model/doctor.py`

**Checkpoint**: The runtime foundation is ready; user story work can proceed in priority order.

---

## Phase 3: User Story 1 - Launch supported models from the CLI (Priority: P1) 🎯 MVP

**Goal**: Let operators target any registered model alias from one stable `local-model` command shape.

**Independent Test**: Launch two registered model aliases through the same CLI flow and confirm the selected model changes while the command family stays the same.

### Validation for User Story 1

- [X] T013 [US1] Capture the manual alias-switching smoke flow in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`

### Implementation for User Story 1

- [X] T014 [P] [US1] Define stock runtime presets and baseline manifest fields in `configs/presets.yaml` and `models/manifests/template.yaml`
- [X] T015 [P] [US1] Implement the stock MLX runner in `src/local_model/runners/mlx_runner.py`
- [X] T016 [US1] Implement `local-model run`, `local-model chat`, and `local-model list-models` alias selection flows in `src/local_model/cli.py`
- [X] T017 [US1] Surface the selected model alias and active runtime path in `src/local_model/services/diagnostics.py` and `src/local_model/cli.py`

**Checkpoint**: User Story 1 is complete when the CLI can switch registered models without changing command families.

---

## Phase 4: User Story 2 - Install and register supported models (Priority: P2)

**Goal**: Allow operators to add supported models through canonical CLI install/register flows so new models become discoverable automatically.

**Independent Test**: Install a supported model through `local-model install`, confirm its metadata is registered, and then target it through the existing model-selection flow.

### Validation for User Story 2

- [X] T018 [US2] Capture the manual install/register smoke flow in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`

### Implementation for User Story 2

- [X] T019 [P] [US2] Define install source metadata and manifest template fields in `configs/models.yaml` and `models/manifests/template.yaml`
- [X] T020 [P] [US2] Implement model download, import, and cache placement flows in `src/local_model/downloads.py` and `src/local_model/services/install_service.py`
- [X] T021 [US2] Implement `local-model install` and `local-model register` commands in `src/local_model/cli.py`
- [X] T022 [US2] Persist registered model metadata and dynamic discovery rules in `src/local_model/registry.py` and `models/manifests/README.md`

**Checkpoint**: User Story 2 is complete when a newly installed model becomes targetable without source-code changes.

---

## Phase 5: User Story 3 - Enable TurboQuant runs (Priority: P3)

**Goal**: Allow the same generation flow to run through the optional TurboQuant backend for compatible models.

**Independent Test**: Launch a compatible registered model with TurboQuant enabled and confirm generation succeeds while the active runtime path is shown before token generation.

### Validation for User Story 3

- [X] T023 [US3] Capture the manual TurboQuant run flow in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`

### Implementation for User Story 3

- [X] T024 [P] [US3] Add TurboQuant preset data and compatibility manifest fields in `configs/presets.yaml` and `models/manifests/template.yaml`
- [X] T025 [P] [US3] Implement the TurboQuant adapter and fork bridge in `src/local_model/runners/turbo_runner.py` and `forks/mlx_turboquant/README.md`
- [X] T026 [US3] Wire TurboQuant runtime selection through the CLI in `src/local_model/cli.py`
- [X] T027 [US3] Emit active TurboQuant runtime notices in `src/local_model/services/diagnostics.py`

**Checkpoint**: User Story 3 is complete when TurboQuant can be selected without changing the surrounding operator flow.

---

## Phase 6: User Story 4 - Preserve safe fallback behavior (Priority: P4)

**Goal**: Keep sessions usable and diagnosable when TurboQuant is unavailable, unsupported, or misconfigured.

**Independent Test**: Request TurboQuant in an unsupported or unavailable environment and confirm the system either falls back to stock MLX with a clear notice or stops before generation with an actionable message.

### Validation for User Story 4

- [X] T028 [US4] Capture the fallback and invalid-manifest smoke flow in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`

### Implementation for User Story 4

- [X] T029 [P] [US4] Encode fallback policy and unsupported-model guidance in `configs/presets.yaml` and `models/manifests/README.md`
- [X] T030 [P] [US4] Implement compatibility preflight and stock fallback logic in `src/local_model/services/runtime_resolver.py`
- [X] T031 [US4] Implement actionable fallback and invalid-registration messages in `src/local_model/cli.py` and `src/local_model/doctor.py`

**Checkpoint**: User Story 4 is complete when TurboQuant failures never leave the user without an explicit outcome.

---

## Phase 7: User Story 5 - Access the runtime from UI and third-party clients (Priority: P5)

**Goal**: Expose the same runtime through a plain MLX UI shell and an OpenAI-compatible local API.

**Independent Test**: Launch the plain MLX UI shell and send one OpenAI-compatible request to the local API, then confirm both surfaces expose the same registered models and runtime-path behavior.

### Validation for User Story 5

- [X] T032 [US5] Capture the plain UI shell and local API smoke flow in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`

### Implementation for User Story 5

- [X] T033 [P] [US5] Implement the local OpenAI-compatible API and request schemas in `src/local_model/api/server.py` and `src/local_model/api/schemas.py`
- [X] T034 [P] [US5] Scaffold the plain MLX UI shell in `apps/macos-ui/Package.swift` and `apps/macos-ui/Sources/LocalModelApp/App.swift`
- [X] T035 [US5] Implement `local-model serve` and `local-model ui` command wiring in `src/local_model/cli.py` and `scripts/launch_ui.sh`
- [X] T036 [US5] Surface registered models and active runtime state in `apps/macos-ui/Sources/LocalModelApp/ViewModels/RuntimeViewModel.swift` and `src/local_model/api/server.py`

**Checkpoint**: User Story 5 is complete when UI and API clients share one runtime contract and model registry.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Finish operator documentation, command help, and end-to-end smoke guidance.

- [X] T037 [P] Document setup, CLI commands, and cache policy in `README.md`
- [X] T038 [P] Document manifest authoring and registration rules in `models/manifests/README.md`
- [X] T039 Consolidate the end-to-end install, run, TurboQuant, fallback, UI, and API smoke flows in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`
- [X] T040 Normalize final CLI help text and operator-facing output wording in `src/local_model/cli.py` and `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and can start immediately.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- User Story 1 (Phase 3) depends on Foundational and establishes the baseline CLI model-targeting flow.
- User Story 2 (Phase 4) depends on User Story 1 because newly installed models must be targetable through the existing CLI flow.
- User Story 3 (Phase 5) depends on User Stories 1 and 2 because TurboQuant runs operate on registered models through the shared CLI.
- User Story 4 (Phase 6) depends on User Story 3 because fallback logic is defined around the optional TurboQuant runtime.
- User Story 5 (Phase 7) depends on User Stories 1 through 4 so the UI shell and API expose the same discovery, runtime selection, and fallback behavior.
- Polish (Phase 8) depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: First deliverable and MVP; no story dependencies after Foundational.
- **US2 (P2)**: Builds on US1 so installed models can be targeted through the existing command flow.
- **US3 (P3)**: Builds on US1-US2 so TurboQuant runs operate on registered models and shared presets.
- **US4 (P4)**: Builds on US3 because fallback behavior is specific to the optional TurboQuant path.
- **US5 (P5)**: Reuses the CLI/runtime contract from US1-US4 for the UI shell and API.

### Within Each User Story

- Capture the manual smoke flow before declaring the story complete.
- Update presets, manifests, or metadata before wiring story-specific runtime behavior.
- Implement runtime and service changes before CLI, API, or UI integration.
- Finish operator-facing diagnostics before closing the story.

### Parallel Opportunities

- T003-T006 can run in parallel during Setup.
- T008-T011 can run in parallel during Foundational.
- In US1, T014-T015 can run in parallel before CLI integration in T016.
- In US2, T019-T020 can run in parallel before CLI command wiring in T021.
- In US3, T024-T025 can run in parallel before CLI selection wiring in T026.
- In US4, T029-T030 can run in parallel before final fallback messaging in T031.
- In US5, T033-T034 can run in parallel before command wiring and UI state integration in T035-T036.
- In Polish, T037-T038 can run in parallel before the final consolidated quickstart pass in T039.

---

## Parallel Example: User Story 2

```bash
Task: "Define install source metadata and manifest template fields in configs/models.yaml and models/manifests/template.yaml"
Task: "Implement model download, import, and cache placement flows in src/local_model/downloads.py and src/local_model/services/install_service.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add TurboQuant preset data and compatibility manifest fields in configs/presets.yaml and models/manifests/template.yaml"
Task: "Implement the TurboQuant adapter and fork bridge in src/local_model/runners/turbo_runner.py and forks/mlx_turboquant/README.md"
```

## Parallel Example: User Story 5

```bash
Task: "Implement the local OpenAI-compatible API and request schemas in src/local_model/api/server.py and src/local_model/api/schemas.py"
Task: "Scaffold the plain MLX UI shell in apps/macos-ui/Package.swift and apps/macos-ui/Sources/LocalModelApp/App.swift"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Confirm the alias-switching smoke flow in `specs/001-mlx-lm-turboquant-kvcache/quickstart.md`.
5. Stop and review before expanding into install/register, TurboQuant, fallback, and UI/API work.

### Incremental Delivery

1. Deliver Setup and Foundational so the runtime skeleton, registry, and install services are stable.
2. Deliver US1 to establish the baseline CLI model-targeting flow.
3. Deliver US2 to make new models dynamically discoverable through canonical install/register flows.
4. Deliver US3 to add the optional TurboQuant backend.
5. Deliver US4 to harden fallback and diagnostics.
6. Deliver US5 to expose the same runtime through the plain UI shell and API.
7. Finish with Phase 8 documentation and smoke-flow cleanup.

### Parallel Team Strategy

1. One engineer completes Setup and Foundational first.
2. After foundation is stable, runtime, manifest, and UI/API work can split along `[P]` tasks inside each story.
3. Merge story slices only after the story’s manual smoke flow and operator-facing output are both updated.

---

## Notes

- All tasks follow the required checklist format with task IDs, optional parallel markers, required story labels, and concrete file paths.
- The feature `plan.md` is still template-shaped, so task paths are grounded in `PLAN.md`, the clarified `spec.md`, and the project constitution.
- Benchmarking and a fixed validation matrix are intentionally excluded from this task list per the clarified feature scope.
