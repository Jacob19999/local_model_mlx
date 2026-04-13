# Feature Specification: Install Nemotron 3 Nano 30B A3B

**Feature Branch**: `002-install-nemotron-3-nano`  
**Created**: 2026-04-12  
**Status**: Draft  
**Input**: User description: "install Nemotron 3 Nano 30B A3B"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the model through the canonical CLI (Priority: P1)

As a local model operator, I can install Nemotron 3 Nano 30B A3B through the existing `local-model install` workflow so I do not need a one-off manual import process for this model.

**Why this priority**: The core request is successful first-party installation of this named model through the project’s standard install path.

**Independent Test**: Can be fully tested by running the documented install flow for this model and confirming that the install completes with a registered model entry and a populated local cache destination.

**Acceptance Scenarios**:

1. **Given** a reachable supported source for Nemotron 3 Nano 30B A3B, **When** the operator runs the standard install workflow for this model, **Then** the system stores the model artifacts in the local cache, writes or updates the model registration metadata, and reports a successful install.
2. **Given** the operator starts an install for this model using an alias that already maps to a different registered model, **When** the conflict is detected, **Then** the system stops before changing the existing registration and explains how to resolve the conflict.

---

### User Story 2 - Discover and launch the installed model (Priority: P2)

As a local model operator, I can see and target Nemotron 3 Nano 30B A3B through the same discovery and run surfaces used for other supported models so the model behaves like a first-class installed option.

**Why this priority**: Installation only delivers value if the new model becomes discoverable and launchable without manual metadata edits.

**Independent Test**: Can be fully tested by installing the model, confirming it appears in the model discovery flow, and launching a generation session by alias through the existing runtime surface.

**Acceptance Scenarios**:

1. **Given** Nemotron 3 Nano 30B A3B has been installed successfully, **When** the operator lists available models or a client queries local model discovery, **Then** the model appears with its registered alias and is marked as selectable.
2. **Given** the installed model appears in discovery, **When** the operator starts a run or chat session for that alias, **Then** the session begins through the supported runtime path without requiring manual file moves or manifest edits.

---

### User Story 3 - Fail safely when installation or runtime prerequisites are not met (Priority: P3)

As a local model operator, I can receive actionable feedback when this model cannot be installed or used so I do not end up with a misleading or partially registered state.

**Why this priority**: Large-model onboarding is risky without clear failure handling for incomplete downloads, incompatible runtime requests, or broken registrations.

**Independent Test**: Can be fully tested by simulating an unavailable source, an interrupted install, and an unsupported runtime request, then confirming the model is not exposed as ready until the issue is resolved.

**Acceptance Scenarios**:

1. **Given** the install source is unavailable, incomplete, or interrupted, **When** the install flow fails, **Then** the system does not expose the model as a runnable registered model and returns a recovery-oriented error.
2. **Given** the model is installed but the requested runtime path is unavailable or unsupported for its registration metadata, **When** the operator starts a session, **Then** the system reports the active fallback or the blocking incompatibility before generation begins.

### Edge Cases

- What happens when the install is interrupted after some model files have been written to the cache but before registration completes?
- How does the system handle a user-selected alias that already belongs to a different registered model?
- What happens when the upstream source resolves successfully but does not contain the full artifact set required for this model?
- How does the system handle insufficient local storage or write permission during model installation?
- What happens when a user requests an optional runtime path for this model that the registration metadata does not allow?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow operators to install Nemotron 3 Nano 30B A3B through the existing `local-model install` workflow without requiring a separate manual registration procedure.
- **FR-002**: The system MUST assign this model a stable user-facing alias so it can be targeted consistently across install, discovery, and run flows.
- **FR-003**: The system MUST place downloaded or imported model artifacts for this model under the local cache location used for installed models and keep those artifacts separate from committed metadata.
- **FR-004**: The system MUST create or update registration metadata for this model only after the install has produced a valid runnable local artifact set.
- **FR-005**: The system MUST expose this model through the existing discovery surfaces after a successful install, including the standard local model-listing flow.
- **FR-006**: Users MUST be able to start a generation session for this model through the same alias-driven run or chat workflow used for other supported models.
- **FR-007**: The system MUST record this model’s supported runtime choices and default runtime behavior in its registration metadata.
- **FR-008**: The system MUST prevent a failed, incomplete, or conflicting install attempt from replacing or corrupting an existing registered model entry.
- **FR-009**: The system MUST provide actionable user-visible errors for source access failures, incomplete artifact sets, alias conflicts, and insufficient local environment prerequisites.
- **FR-010**: The system MUST tell users before generation whether this model will run through its default runtime path, an allowed fallback path, or not run because the requested runtime is unsupported.

### Runtime, CLI & Observability Requirements

- **RCO-001**: This feature affects `local-model install`, `local-model list-models`, `local-model run`, and `local-model chat`; it MUST not require a new command family for Nemotron 3 Nano 30B A3B.
- **RCO-002**: The required runtime path in scope is the stock MLX path used by installed models, while any optional alternate runtime remains subject to the model’s registration metadata and existing fallback policy when optional dependencies are unavailable.
- **RCO-003**: Any committed metadata for this model MUST remain in lightweight files under `configs/` and `models/manifests/`, while downloaded weights or imported artifacts remain under `models/cache/`.
- **RCO-004**: User-visible install and preflight output MUST identify the model alias, source location, cache destination, registration outcome, and any fallback or blocking reason needed to diagnose local setup issues.

### Key Entities *(include if feature involves data)*

- **Model Registration**: The lightweight record that binds Nemotron 3 Nano 30B A3B to a stable alias, its source information, its cache destination, and its allowed runtime choices.
- **Install Attempt**: A single user-initiated workflow that acquires the model artifacts, validates them, and either produces a successful registration or a clean failure state.
- **Model Alias**: The user-facing identifier used to select this model consistently across install, listing, and inference flows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful installs for Nemotron 3 Nano 30B A3B result in exactly one discoverable registered model entry and a corresponding local cache destination with no manual metadata editing.
- **SC-002**: After a successful install, the model appears in the standard local discovery flow before the user performs any source-code change or manual manifest authoring.
- **SC-003**: 100% of failed or interrupted install attempts leave the model unavailable for selection until a complete install succeeds.
- **SC-004**: A user can move from successful install to a first run or chat session for this model in the same local environment using only the documented alias-based CLI flow.
- **SC-005**: 100% of runtime start attempts for this model report the active runtime path, fallback state, or blocking incompatibility before first-token generation begins.

## Assumptions

- A supported upstream source for Nemotron 3 Nano 30B A3B is available through one of the project’s existing install source types.
- This feature adds first-party support for one named model and does not introduce a new generic installer beyond the existing install and registration workflow.
- Initial scope is limited to local text-generation use of this model through the existing CLI and discovery surfaces.
- Successful installation still depends on the operator having sufficient local storage, filesystem permissions, and any baseline dependencies already required by the stock MLX workflow.
- Optional alternate runtime selection for this model follows the project’s existing compatibility and fallback policy rather than redefining runtime behavior specifically for this model.
