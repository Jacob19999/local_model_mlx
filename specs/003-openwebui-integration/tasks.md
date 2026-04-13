---

description: "Task list for implementing Replace macOS UI with Open WebUI"

---

# Tasks: Replace macOS UI with Open WebUI

**Input**: Design documents from `/specs/003-openwebui-integration/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`

**Tests & Validation**: Add targeted `pytest` coverage for the retired `local-model ui` behavior and preserve manual smoke validation for `serve`, `/v1/models`, `/v1/chat/completions`, and the documented Open WebUI onboarding flow.

**Organization**: Tasks are grouped by user story so each increment remains independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the shared test scaffolding needed for the Open WebUI migration work.

- [X] T001 Add shared Open WebUI migration fixtures and documentation-assertion helpers in `tests/conftest.py`
- [X] T002 [P] Create feature-specific migration test modules in `tests/contract/test_cli_openwebui_migration.py`, `tests/contract/test_api_openwebui_compat.py`, and `tests/integration/test_openwebui_onboarding_docs.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Remove the retired launcher surface and establish the shared migration behavior every story depends on.

**⚠️ CRITICAL**: Complete this phase before starting user story work.

- [X] T003 Define shared Open WebUI endpoint constants and retired-UI migration message helpers in `src/local_model/cli.py`
- [X] T004 [P] Remove the retired native UI launcher assets from `scripts/launch_ui.sh`, `apps/macos-ui/Package.swift`, `apps/macos-ui/Sources/LocalModelApp/App.swift`, and `apps/macos-ui/Sources/LocalModelApp/ViewModels/RuntimeViewModel.swift`

**Checkpoint**: The native launcher surface is retired and the CLI can be redirected to the supported migration path.

---

## Phase 3: User Story 1 - Use the local API through a supported modern UI (Priority: P1) 🎯 MVP

**Goal**: Let operators connect Open WebUI to the existing local service and complete a chat round trip without depending on the native macOS shell.

**Independent Test**: Start the local service, follow the documented Open WebUI onboarding flow, confirm a registered model appears in the UI, and complete one chat request through the existing API.

### Validation for User Story 1

- [X] T005 [P] [US1] Add CLI contract coverage for `local-model ui` migration guidance and non-zero exit behavior in `tests/contract/test_cli_openwebui_migration.py`
- [X] T006 [P] [US1] Add API contract coverage for `GET /v1/models` and `POST /v1/chat/completions` compatibility in `tests/contract/test_api_openwebui_compat.py`

### Implementation for User Story 1

- [X] T007 [US1] Rewire `local-model ui` to print Open WebUI onboarding guidance instead of launching SwiftUI in `src/local_model/cli.py`
- [X] T008 [US1] Document the supported Open WebUI connection flow and `http://127.0.0.1:8000/v1` settings in `README.md` and `specs/003-openwebui-integration/contracts/openwebui-onboarding.md`
- [X] T009 [US1] Capture the serve, connect, model discovery, and first-chat smoke flow in `specs/003-openwebui-integration/quickstart.md`

**Checkpoint**: User Story 1 is complete when the CLI redirects operators to Open WebUI and the documented onboarding flow reaches a successful chat round trip.

---

## Phase 4: User Story 2 - Understand the supported operator path (Priority: P2)

**Goal**: Make the repository’s supported interactive workflow unambiguous by removing conflicting native-UI guidance and pointing operators to Open WebUI plus the local service.

**Independent Test**: Review a clean checkout and confirm the README, AGENTS guidance, and feature contracts all point to `local-model serve` plus Open WebUI rather than the retired native macOS shell.

### Validation for User Story 2

- [X] T010 [P] [US2] Add documentation integration coverage that supported-surface guidance no longer points to the retired native UI in `tests/integration/test_openwebui_onboarding_docs.py`

### Implementation for User Story 2

- [X] T011 [US2] Rewrite repository interactive-workflow guidance and prerequisites around Open WebUI in `README.md` and `AGENTS.md`
- [X] T012 [US2] Rewrite the supported operator-path contract and migration rationale in `specs/003-openwebui-integration/contracts/local-model-cli.md` and `specs/003-openwebui-integration/research.md`
- [X] T013 [US2] Delete the retired native UI project tree in `apps/macos-ui/` and remove any remaining launcher references in `scripts/launch_ui.sh`

**Checkpoint**: User Story 2 is complete when no maintained repository entry point tells operators to build or launch the retired macOS UI.

---

## Phase 5: User Story 3 - Avoid broken migration states (Priority: P3)

**Goal**: Give operators clear recovery guidance when the service is down, the endpoint is wrong, or no models are visible after the UI migration.

**Independent Test**: Attempt the supported workflow with the service stopped, with no visible models, and with an incorrect service address, then confirm the CLI and docs explain how to identify and correct each issue.

### Validation for User Story 3

- [X] T014 [P] [US3] Extend CLI contract coverage for wrong-endpoint, service-down, and no-model recovery hints in `tests/contract/test_cli_openwebui_migration.py`
- [X] T015 [P] [US3] Extend documentation integration coverage for troubleshooting and verification commands in `tests/integration/test_openwebui_onboarding_docs.py`

### Implementation for User Story 3

- [X] T016 [US3] Add recovery guidance for stopped service, incorrect endpoint, and empty model lists in `README.md` and `specs/003-openwebui-integration/contracts/openwebui-onboarding.md`
- [X] T017 [US3] Document verification and troubleshooting commands for `/health` and `/v1/models` in `specs/003-openwebui-integration/quickstart.md` and `specs/003-openwebui-integration/contracts/local-model-api.md`
- [X] T018 [US3] Refine the `local-model ui` migration notice with actionable recovery wording in `src/local_model/cli.py`

**Checkpoint**: User Story 3 is complete when common misconfiguration and availability failures have explicit recovery guidance across both the CLI and operator docs.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reconcile final terminology and validate the complete migration workflow.

- [X] T019 Reconcile final supported-surface terminology across `README.md`, `specs/003-openwebui-integration/spec.md`, and `specs/003-openwebui-integration/plan.md`
- [X] T020 Run the Open WebUI migration smoke workflow and record final validation notes in `specs/003-openwebui-integration/quickstart.md` and `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and can start immediately.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- User Story 1 (Phase 3) depends on Foundational and delivers the MVP Open WebUI migration path.
- User Story 2 (Phase 4) depends on User Story 1 because the final repository guidance must point at the implemented onboarding flow.
- User Story 3 (Phase 5) depends on User Stories 1 and 2 because troubleshooting guidance builds on the final CLI migration behavior and supported docs.
- Polish (Phase 6) depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: First deliverable and MVP; no story dependencies after Foundational.
- **US2 (P2)**: Builds on US1 so documentation points to the implemented Open WebUI onboarding path.
- **US3 (P3)**: Builds on US1-US2 so recovery guidance matches the final CLI and documentation surfaces.

### Within Each User Story

- Add validation coverage before closing the story.
- Implement shared CLI behavior before documenting operator-facing workflows.
- Update onboarding and troubleshooting documents before running the final smoke capture.
- Finish recovery wording before closing the story.

### Parallel Opportunities

- T001-T002 can proceed in parallel once the shared test layout is agreed.
- T003-T004 can proceed in parallel during Foundational because the CLI migration helper and retired asset removal target separate files.
- In US1, T005-T006 can run in parallel, and T008-T009 can run in parallel after T007 establishes the CLI redirect.
- In US2, T010 can run alongside T011-T012, while T013 can land once the removal scope is confirmed.
- In US3, T014-T015 can run in parallel, and T016-T017 can run in parallel before T018 finalizes the CLI recovery notice.

---

## Parallel Example: User Story 1

```bash
Task: "Add CLI contract coverage for local-model ui migration guidance and non-zero exit behavior in tests/contract/test_cli_openwebui_migration.py"
Task: "Add API contract coverage for GET /v1/models and POST /v1/chat/completions compatibility in tests/contract/test_api_openwebui_compat.py"

Task: "Document the supported Open WebUI connection flow and http://127.0.0.1:8000/v1 settings in README.md and specs/003-openwebui-integration/contracts/openwebui-onboarding.md"
Task: "Capture the serve, connect, model discovery, and first-chat smoke flow in specs/003-openwebui-integration/quickstart.md"
```

## Parallel Example: User Story 2

```bash
Task: "Add documentation integration coverage that supported-surface guidance no longer points to the retired native UI in tests/integration/test_openwebui_onboarding_docs.py"
Task: "Rewrite the supported operator-path contract and migration rationale in specs/003-openwebui-integration/contracts/local-model-cli.md and specs/003-openwebui-integration/research.md"
```

## Parallel Example: User Story 3

```bash
Task: "Extend CLI contract coverage for wrong-endpoint, service-down, and no-model recovery hints in tests/contract/test_cli_openwebui_migration.py"
Task: "Extend documentation integration coverage for troubleshooting and verification commands in tests/integration/test_openwebui_onboarding_docs.py"

Task: "Add recovery guidance for stopped service, incorrect endpoint, and empty model lists in README.md and specs/003-openwebui-integration/contracts/openwebui-onboarding.md"
Task: "Document verification and troubleshooting commands for /health and /v1/models in specs/003-openwebui-integration/quickstart.md and specs/003-openwebui-integration/contracts/local-model-api.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the documented Open WebUI onboarding flow from `specs/003-openwebui-integration/quickstart.md`.
5. Stop and review before broad documentation cleanup and troubleshooting hardening.

### Incremental Delivery

1. Deliver Setup and Foundational so the CLI redirect and retired asset removal are in place.
2. Deliver US1 to establish the supported Open WebUI onboarding path.
3. Deliver US2 to remove conflicting native-UI guidance across maintained docs and contracts.
4. Deliver US3 to harden troubleshooting and recovery guidance.
5. Finish with Phase 6 terminology cleanup and full smoke validation.

### Parallel Team Strategy

1. One engineer completes Setup and Foundational first.
2. After foundation is stable, contract tests, API compatibility tests, and documentation updates can split along `[P]` tasks.
3. Merge each story only after its tests and quickstart validation are both updated.

---

## Notes

- All tasks follow the required checklist format with task IDs, optional `[P]` markers, required story labels for story phases, and explicit file paths.
- Suggested MVP scope: Phase 3 / User Story 1 only.
- Total tasks: 20.
- Story task counts: US1 = 5, US2 = 4, US3 = 5.
