---

description: "Task list for implementing Install Nemotron 3 Nano 30B A3B"
---

# Tasks: Install Nemotron 3 Nano 30B A3B

**Input**: Design documents from `/specs/002-install-nemotron-3-nano/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`

**Tests & Validation**: Add targeted Python unit, integration, and contract coverage under `tests/` for install, registry, discovery, and runtime-preflight behavior. Keep the manual smoke evidence in `specs/002-install-nemotron-3-nano/quickstart.md`.

**Organization**: Tasks are grouped by user story so each increment remains independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the missing test scaffolding and reusable fixtures needed for feature delivery.

- [x] T001 Configure pytest collection and shared test package scaffolding in `pyproject.toml`, `tests/conftest.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`, and `tests/contract/__init__.py`
- [x] T002 [P] Add reusable install-validation fixtures and fixture documentation in `tests/fixtures/README.md` and `tests/fixtures/manifests/invalid_nemotron.yaml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared validation and manifest infrastructure required by every story.

**⚠️ CRITICAL**: Complete this phase before starting user story work.

- [x] T003 Add install-attempt and runtime-preflight dataclasses for validation state in `src/local_model/models.py`
- [x] T004 [P] Implement manifest lookup, alias-conflict detection, and validation helpers in `src/local_model/registry.py`
- [x] T005 [P] Implement cache-destination writability and artifact-set validation helpers in `src/local_model/downloads.py`
- [x] T006 [P] Wire validated install state transitions and rollback-safe manifest writes in `src/local_model/services/install_service.py`
- [x] T007 [P] Expand prerequisite and operator diagnostics for `huggingface_hub`, cache paths, and manifest health in `src/local_model/doctor.py` and `src/local_model/services/diagnostics.py`

**Checkpoint**: Install validation, manifest safety, and shared diagnostics are ready for story work.

---

## Phase 3: User Story 1 - Install the model through the canonical CLI (Priority: P1) 🎯 MVP

**Goal**: Let operators install Nemotron 3 Nano 30B A3B through the existing `local-model install` workflow without manual manifest authoring.

**Independent Test**: Run the documented Nemotron install flow against the canonical Hugging Face repo and confirm the install succeeds with exactly one registered alias and a populated cache destination; then trigger an alias conflict and confirm no existing registration is changed.

### Validation for User Story 1

- [x] T008 [P] [US1] Add unit coverage for canonical source selection and Nemotron manifest defaults in `tests/unit/test_nemotron_manifest_defaults.py`
- [x] T009 [P] [US1] Add install integration coverage for successful Nemotron installs and alias conflicts in `tests/integration/test_nemotron_install.py`
- [x] T010 [P] [US1] Add CLI contract coverage for install JSON output and stderr failures in `tests/contract/test_cli_nemotron_install.py`

### Implementation for User Story 1

- [x] T011 [P] [US1] Add canonical Nemotron source metadata and manifest defaults in `configs/models.yaml` and `models/manifests/template.yaml`
- [x] T012 [P] [US1] Implement `hf_repo` install validation, partial-download rejection, and conflict-safe destination handling in `src/local_model/downloads.py` and `src/local_model/services/install_service.py`
- [x] T013 [US1] Implement Nemotron install registration and success/failure output wiring in `src/local_model/registry.py` and `src/local_model/cli.py`
- [x] T014 [US1] Capture the canonical install smoke flow and alias-conflict recovery steps in `specs/002-install-nemotron-3-nano/quickstart.md`

**Checkpoint**: User Story 1 is complete when Nemotron installs cleanly through `local-model install` and conflicting installs fail without mutating the existing registration.

---

## Phase 4: User Story 2 - Discover and launch the installed model (Priority: P2)

**Goal**: Make a successfully installed Nemotron model show up in discovery and run through the standard alias-driven CLI and API surfaces.

**Independent Test**: Install Nemotron once, confirm it appears in `local-model list-models` and `GET /v1/models`, then launch one CLI run or chat session through the alias and verify stock MLX preflight and generation succeed without manual edits.

### Validation for User Story 2

- [x] T015 [P] [US2] Add integration coverage for Nemotron manifest discovery and stock-MLX runs in `tests/integration/test_nemotron_discovery_run.py`
- [x] T016 [P] [US2] Add API contract coverage for `/v1/models` and `/v1/chat/completions` Nemotron responses in `tests/contract/test_api_nemotron.py`

### Implementation for User Story 2

- [x] T017 [P] [US2] Add Nemotron display metadata, tags, and API visibility guidance in `models/manifests/template.yaml` and `models/manifests/README.md`
- [x] T018 [P] [US2] Implement manifest-backed discovery summaries and runtime banner data for Nemotron in `src/local_model/registry.py` and `src/local_model/services/diagnostics.py`
- [x] T019 [P] [US2] Implement stock-MLX execution and runtime selection support for the Nemotron manifest in `src/local_model/runners/mlx_runner.py` and `src/local_model/services/runtime_resolver.py`
- [x] T020 [US2] Wire Nemotron discovery and alias-driven run/chat flows through `local-model list-models`, `run`, and `chat` in `src/local_model/cli.py`
- [x] T021 [US2] Expose Nemotron through `/v1/models` and chat completions in `src/local_model/api/schemas.py` and `src/local_model/api/server.py`
- [x] T022 [US2] Capture the discovery and first-run smoke flow in `specs/002-install-nemotron-3-nano/quickstart.md`

**Checkpoint**: User Story 2 is complete when the installed alias becomes visible to CLI and API discovery and can be launched through the stock MLX path.

---

## Phase 5: User Story 3 - Fail safely when installation or runtime prerequisites are not met (Priority: P3)

**Goal**: Prevent incomplete installs and unsupported runtime selections from appearing runnable, and return actionable recovery guidance before generation starts.

**Independent Test**: Simulate an unavailable or interrupted install, insufficient write access, and an unsupported `--runtime turboquant --no-fallback` request; confirm no runnable registration is exposed and every failure reports a recovery-oriented reason before first-token generation.

### Validation for User Story 3

- [x] T023 [P] [US3] Add unit coverage for install validation and runtime preflight failures in `tests/unit/test_install_validation.py` and `tests/unit/test_runtime_resolver_nemotron.py`
- [x] T024 [P] [US3] Add CLI contract coverage for interrupted installs and `--no-fallback` runtime errors in `tests/contract/test_cli_nemotron_failures.py`

### Implementation for User Story 3

- [x] T025 [P] [US3] Implement incomplete-artifact, permission, and source-access failure handling in `src/local_model/downloads.py` and `src/local_model/services/install_service.py`
- [x] T026 [P] [US3] Implement explicit fallback and blocking notices for unsupported Nemotron runtime requests in `src/local_model/services/runtime_resolver.py` and `src/local_model/services/diagnostics.py`
- [x] T027 [US3] Surface safe-failure behavior through CLI, doctor, and API error responses in `src/local_model/cli.py`, `src/local_model/doctor.py`, and `src/local_model/api/server.py`
- [x] T028 [US3] Capture interrupted-install, insufficient-permission, and unsupported-runtime smoke flows in `specs/002-install-nemotron-3-nano/quickstart.md`

**Checkpoint**: User Story 3 is complete when failed installs never become discoverable and unsupported runtime requests stop or fall back before generation begins.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize operator-facing documentation and reconcile the end-to-end workflow with the contracts.

- [x] T029 [P] Update operator documentation for Nemotron install, discovery, and runtime policy in `README.md`
- [x] T030 [P] Document final manifest authoring, alias-conflict, and recovery rules in `models/manifests/README.md`
- [x] T031 Run the full Nemotron quickstart and reconcile final contract examples in `specs/002-install-nemotron-3-nano/quickstart.md`, `specs/002-install-nemotron-3-nano/contracts/local-model-cli.md`, and `specs/002-install-nemotron-3-nano/contracts/local-model-api.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and can start immediately.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- User Story 1 (Phase 3) depends on Foundational and establishes the validated install path.
- User Story 2 (Phase 4) depends on User Story 1 because discovery and launch require a successful registration flow.
- User Story 3 (Phase 5) depends on User Stories 1 and 2 because safe-failure behavior extends the install and runtime paths already in place.
- Polish (Phase 6) depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: First deliverable and MVP; no story dependencies after Foundational.
- **US2 (P2)**: Builds on US1 so installed Nemotron manifests become discoverable and runnable.
- **US3 (P3)**: Builds on US1-US2 so incomplete installs and unsupported runtime requests can be rejected against the final registration and discovery flow.

### Within Each User Story

- Add validation coverage before closing the story.
- Update manifest or config data before wiring story-specific CLI or API behavior.
- Complete service and runtime logic before final operator-facing output.
- Refresh the quickstart smoke flow before marking the story done.

### Parallel Opportunities

- T001-T002 can proceed in parallel once the desired test layout is agreed.
- T004-T007 can proceed in parallel during Foundational because they target separate shared modules.
- In US1, T008-T010 can run in parallel, and T011-T012 can run in parallel before T013 integrates the install flow.
- In US2, T015-T016 can run in parallel, and T017-T019 can run in parallel before T020-T021 integrate CLI and API surfaces.
- In US3, T023-T024 can run in parallel, and T025-T026 can run in parallel before T027 integrates the final error surfaces.
- In Polish, T029-T030 can run in parallel before T031 completes the final end-to-end reconciliation.

---

## Parallel Example: User Story 1

```bash
Task: "Add install integration coverage for successful Nemotron installs and alias conflicts in tests/integration/test_nemotron_install.py"
Task: "Add CLI contract coverage for install JSON output and stderr failures in tests/contract/test_cli_nemotron_install.py"

Task: "Add canonical Nemotron source metadata and manifest defaults in configs/models.yaml and models/manifests/template.yaml"
Task: "Implement hf_repo install validation, partial-download rejection, and conflict-safe destination handling in src/local_model/downloads.py and src/local_model/services/install_service.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add API contract coverage for /v1/models and /v1/chat/completions Nemotron responses in tests/contract/test_api_nemotron.py"
Task: "Add integration coverage for Nemotron manifest discovery and stock-MLX runs in tests/integration/test_nemotron_discovery_run.py"

Task: "Add Nemotron display metadata, tags, and API visibility guidance in models/manifests/template.yaml and models/manifests/README.md"
Task: "Implement stock-MLX execution and runtime selection support for the Nemotron manifest in src/local_model/runners/mlx_runner.py and src/local_model/services/runtime_resolver.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add unit coverage for install validation and runtime preflight failures in tests/unit/test_install_validation.py and tests/unit/test_runtime_resolver_nemotron.py"
Task: "Add CLI contract coverage for interrupted installs and --no-fallback runtime errors in tests/contract/test_cli_nemotron_failures.py"

Task: "Implement incomplete-artifact, permission, and source-access failure handling in src/local_model/downloads.py and src/local_model/services/install_service.py"
Task: "Implement explicit fallback and blocking notices for unsupported Nemotron runtime requests in src/local_model/services/runtime_resolver.py and src/local_model/services/diagnostics.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the canonical Nemotron install and alias-conflict flows from `specs/002-install-nemotron-3-nano/quickstart.md`.
5. Stop and review before expanding into discovery, launch, and safe-failure hardening.

### Incremental Delivery

1. Deliver Setup and Foundational so validated install and manifest behavior are stable.
2. Deliver US1 to make Nemotron installable through the standard CLI.
3. Deliver US2 to make the installed alias discoverable and runnable through CLI and API surfaces.
4. Deliver US3 to harden failure handling for incomplete installs and unsupported runtime requests.
5. Finish with Phase 6 documentation and end-to-end reconciliation.

### Parallel Team Strategy

1. One engineer completes Setup and Foundational first.
2. After foundation is stable, test-writing and implementation `[P]` tasks can split across separate files inside each story.
3. Merge each story only after its automated coverage and quickstart validation are both updated.

---

## Notes

- All tasks follow the required checklist format with task IDs, optional `[P]` markers, required story labels for story phases, and explicit file paths.
- Suggested MVP scope: Phase 3 / User Story 1 only.
- Total tasks: 31.
- Story task counts: US1 = 7, US2 = 8, US3 = 6.
