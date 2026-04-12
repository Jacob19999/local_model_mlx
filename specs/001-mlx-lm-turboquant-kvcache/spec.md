# Feature Specification: MLX-LM TurboQuant KV Cache

**Feature Branch**: `001-mlx-lm-turboquant-kvcache`  
**Created**: 2026-04-12  
**Status**: Draft  
**Input**: User description: "mlx-lm + the mlx-optiq drop-in TurboQuantKVCache"

## Clarifications

### Session 2026-04-12

- Q: Should benchmarking be part of this feature? → A: No. Benchmarking is out of scope; the feature stays barebones.
- Q: How should users launch different models? → A: Through a simple command-line input that selects the target model.
- Q: What front-end experience is required? → A: A plain MLX front-end UI shell is the required local user interface.
- Q: How should third-party tools access the runtime? → A: Through a standard local API, normalized here as an OpenAI-compatible API for tools such as BrowserOS.
- Q: Should supported model scope stay fixed or expand as new models are installed? → A: Dynamic installed-model discovery; newly installed models must become targetable through the same CLI without code changes.
- Q: How should new models become discoverable to the system? → A: Through canonical `local-model` install or register flows that update model metadata; unregistered cache folders are not treated as supported models.
- Q: Is model installation in scope for this feature or a precondition? → A: In scope; the feature includes a canonical `local-model install` flow that installs and registers supported models, and future installs use the same command.
- Q: Should this feature require a fixed install count or formal validation set? → A: No. There is no fixed model-count requirement or formal validation matrix; the feature only needs a minimal working flow where installed models can be launched through the CLI and surfaced in a plain MLX UI shell.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Launch supported models from the CLI (Priority: P1)

As a local model operator, I can launch different supported models by changing a simple command-line input so I can switch models without learning multiple workflows.

**Why this priority**: The core product value is a minimal local control plane that lets the user start the right model quickly.

**Independent Test**: Can be fully tested by launching two different supported models through the public CLI using the same command shape and confirming that each request runs against the selected model.

**Acceptance Scenarios**:

1. **Given** multiple supported model aliases are configured, **When** the user starts a session with a simple command-line input that names one alias, **Then** the selected model launches without requiring a different command family.
2. **Given** the user changes only the model selection input, **When** the next session starts, **Then** the system runs the newly selected model and clearly identifies it to the user.
3. **Given** a new model is installed and registered through the local model metadata flow, **When** the user targets that alias through the same CLI command shape, **Then** the new model is discoverable and launchable without additional code changes.

---

### User Story 2 - Install and register supported models (Priority: P2)

As a local model operator, I can install and register supported models through the canonical CLI so newly added models become discoverable through the same runtime surfaces.

**Why this priority**: Dynamic model targeting depends on a first-party install and registration path that keeps model metadata consistent and git-safe.

**Independent Test**: Can be fully tested by installing a supported model through `local-model install`, confirming its metadata is registered, and then targeting it from the existing model-selection flow.

**Acceptance Scenarios**:

1. **Given** a supported upstream model source, **When** the user runs `local-model install` with a target alias, **Then** the model is downloaded or linked into the local cache and registered in the model metadata flow.
2. **Given** a model installed through the canonical CLI flow, **When** the user runs the existing model-listing or model-selection commands, **Then** the new model appears without requiring source-code changes or manual cache inspection.

---

### User Story 3 - Enable TurboQuant runs (Priority: P3)

As a local model operator, I can run an MLX-LM text-generation workflow with TurboQuant KV cache enabled so I can use the accelerated path without changing the rest of the interaction flow.

**Why this priority**: The main feature request is the drop-in TurboQuant cache path, but it only matters after a simple launch flow exists.

**Independent Test**: Can be fully tested by launching a supported model with TurboQuant enabled and confirming that generation completes while the active runtime path is shown to the user.

**Acceptance Scenarios**:

1. **Given** a compatible model and an available TurboQuant cache path, **When** the user starts a local generation workflow with TurboQuant enabled, **Then** the request completes successfully and the user is told that the TurboQuant cache path is active.
2. **Given** a compatible model already used in a stock MLX-LM workflow, **When** the user repeats that workflow with TurboQuant enabled, **Then** the prompt and response flow remain consistent with the baseline experience.

---

### User Story 4 - Preserve safe fallback behavior (Priority: P4)

As a local model operator, I can request the TurboQuant path without risking a broken session when the optional runtime is unavailable or incompatible.

**Why this priority**: Experimental acceleration only has value if the standard MLX-LM path remains reliable and users can understand what happened when TurboQuant is not usable.

**Independent Test**: Can be fully tested by requesting the TurboQuant path in an environment where the cache integration is unavailable or unsupported and confirming that the system either falls back to the stock path with a clear notice or stops before generation with an actionable message.

**Acceptance Scenarios**:

1. **Given** the user requests the TurboQuant path and the optional runtime is unavailable, **When** the session starts, **Then** the user receives a clear notice of the degraded mode and the workflow continues through the stock path when fallback is allowed.
2. **Given** the user requests the TurboQuant path for an unsupported model or configuration, **When** the request is validated, **Then** the system identifies the incompatibility before generation and explains the next recovery step.

---

### User Story 5 - Access the runtime from UI and third-party clients (Priority: P5)

As a user or tool integrator, I can access the same local model service from a plain MLX UI shell and from third-party clients through a standard API so there is one consistent local runtime surface.

**Why this priority**: The CLI remains the control plane, but the feature also needs a usable local UI and an automation-friendly API for external tools.

**Independent Test**: Can be fully tested by launching the local UI shell and by sending one request from a third-party client to the local API, then confirming both use the same available models and generation behavior.

**Acceptance Scenarios**:

1. **Given** the local runtime is available, **When** the user opens the plain MLX UI shell, **Then** they can choose a supported model and start a generation session through the same underlying local service.
2. **Given** a third-party client that supports an OpenAI-compatible API, **When** it sends a local text-generation request, **Then** the service accepts the request and returns a response for a supported model.

### Edge Cases

- What happens when the user selects the TurboQuant-enabled path for a model manifest that does not declare compatibility?
- How does the system handle a TurboQuant cache initialization failure after the model has otherwise passed preflight checks?
- What happens when a named preset points to the TurboQuant path on a machine where the optional runtime is not installed?
- What happens when the user names a model alias that is unknown to the local runtime?
- What happens when a newly installed model has incomplete or invalid manifest metadata?
- What happens when model files exist under `models/cache/` without having been installed or registered through the canonical metadata flow?
- How does the system handle a third-party API request when the requested model is not loaded or not supported?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to launch supported models from a simple `local-model` command-line input that selects the target model.
- **FR-002**: The system MUST allow users to invoke an MLX-LM text-generation workflow with TurboQuant KV cache enabled for supported models.
- **FR-003**: The system MUST preserve a stock MLX-LM execution path for the same workflow when TurboQuant KV cache is disabled, unavailable, or unsupported.
- **FR-004**: The system MUST provide a stable user-facing way to choose the target model and whether TurboQuant is enabled without requiring separate command families for each model.
- **FR-005**: The system MUST tell users before generation begins whether the request will run with TurboQuant KV cache, the stock cache path, or a degraded fallback path.
- **FR-006**: Users MUST be able to reuse the same prompt and conversation flow they use for the stock MLX-LM path when the TurboQuant-enabled path is selected.
- **FR-007**: The system MUST identify which models or model manifests are eligible for the TurboQuant-enabled path.
- **FR-008**: The system MUST emit actionable diagnostics when TurboQuant KV cache cannot be used, including whether the request fell back or stopped.
- **FR-009**: The system MUST provide a plain MLX UI shell as a local interface over the same runtime workflows exposed through the CLI.
- **FR-010**: The system MUST expose a standard local API, normalized here as OpenAI-compatible, so third-party clients can list supported models and send text-generation requests.
- **FR-011**: The system MUST keep committed metadata for model selection, runtime selection, and model capability separate from downloaded model weights.
- **FR-012**: The system MUST avoid requiring duplicate model downloads solely to try the TurboQuant-enabled path for an already supported model.
- **FR-013**: The system MUST discover newly installed models from committed metadata or local registration flows so they can be targeted through the existing CLI, UI, and API surfaces without code changes.
- **FR-014**: The system MUST provide canonical `local-model` install or register flows that create or update model metadata for newly added models; raw cache directories without registration metadata MUST NOT be exposed as supported models.
- **FR-015**: The system MUST support using `local-model install` to add supported models over time, and those models MUST become immediately discoverable through the existing CLI, UI, and API surfaces after successful registration.

### Runtime, CLI & Observability Requirements

- **RCO-001**: This feature affects the `local-model` CLI surface for model launch, chat, UI launch, and local API serving, and it MUST include a stable way to choose the target model and the TurboQuant-enabled path from the command line.
- **RCO-001**: This feature affects the `local-model` CLI surface for model install/register, launch, chat, UI launch, and local API serving, and it MUST include a stable way to choose the target model and the TurboQuant-enabled path from the command line.
- **RCO-002**: The runtime paths in scope are the stock MLX path and an experimental TurboQuant path; when the optional TurboQuant path is unavailable, standard generation workflows MUST degrade to the stock path with clear notice, while the local API and UI continue to reflect the active runtime path.
- **RCO-003**: Any committed metadata changes MUST stay within lightweight configuration or manifest files under `configs/` or `models/manifests/`, while downloaded weights remain under `models/cache/` and are not duplicated just to enable this feature.
- **RCO-004**: User-visible output MUST identify the selected model, the selected runtime path, any fallback decision, API availability, and enough failure detail for a local operator to understand whether the TurboQuant path and local service are usable on their machine.

### Key Entities *(include if feature involves data)*

- **Runtime Preset**: A named user-facing selection that chooses a local launch path, including whether the request targets the stock MLX path or the TurboQuant-enabled path.
- **Model Manifest**: Lightweight metadata describing a model alias, its local storage expectations, API visibility, and whether the TurboQuant-enabled path is supported for that model.
- **Execution Session**: A single user-invoked CLI, UI, or API request that records the requested model, the requested runtime path, the actual runtime path used, and any fallback or failure state.
- **API Request**: A third-party client request sent to the local OpenAI-compatible service for model discovery or text generation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can start any supported model by changing only the model-selection input in the standard CLI flow, with no extra setup beyond the baseline launch command.
- **SC-002**: A user can enable the TurboQuant path for a compatible model with no more than one additional runtime selection step beyond the baseline MLX-LM workflow.
- **SC-003**: 100% of requests that cannot use TurboQuant end with either a successful stock-path fallback or a user-visible diagnostic before first-token generation; no request silently claims TurboQuant use when it is inactive.
- **SC-004**: A third-party client using the local OpenAI-compatible API can successfully discover at least one supported model and complete a text-generation request against that model.
- **SC-005**: After a new model is installed and registered, it becomes available through the existing model-listing and model-selection flows without requiring a new command family or source-code edit.
- **SC-006**: A user can install a supported model through `local-model install`, then target it successfully through the existing CLI flow in the same local environment, with no fixed model-count requirement for the feature.

## Assumptions

- Primary users are local Apple Silicon operators experimenting with MLX-LM and wanting an optional accelerated cache path without losing the baseline workflow.
- Initial scope is limited to text-generation flows; multimodal or vision-specific behavior is out of scope for this feature.
- The public control plane for this project remains the `local-model` CLI described in the repository plan, with simple model selection and runtime selection exposed there first.
- The local UI is a plain MLX-style shell over the same runtime workflows rather than a separate inference implementation.
- Third-party integration is satisfied by a local OpenAI-compatible API for model listing and text generation.
- TurboQuant KV cache remains an optional experimental capability and must not block a functioning stock MLX path.
- The supported model list is intended to grow dynamically over time through local registration and installation flows, with no fixed model-count requirement for this feature.
- Only models added through the canonical CLI install or register flows are considered supported and discoverable by the runtime surfaces.
- Implementation sequencing assumes the MLX and TurboQuant runtime backend is built first, followed by installation and registration flows for supported models through the canonical CLI.
