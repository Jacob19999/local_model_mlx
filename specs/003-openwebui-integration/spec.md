# Feature Specification: Replace macOS UI with Open WebUI

**Feature Branch**: `003-openwebui-integration`  
**Created**: 2026-04-12  
**Status**: Implemented  
**Input**: User description: "Keep local-model serve. Stop investing in apps/macos-ui/ and delete. Add docs or a helper script for Open WebUI pointing at http://127.0.0.1:8000/v1"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use the local API through a supported modern UI (Priority: P1)

As a local model operator, I can connect Open WebUI to the existing local model service so I can use a modern chat interface without depending on the native desktop shell.

**Why this priority**: The main user value is preserving the existing local serving surface while replacing the outdated UI path with a supported modern interface.

**Independent Test**: Can be fully tested by starting the local model service, following the first-party Open WebUI guidance, and confirming that a user can discover a registered model and complete a chat round trip through that UI.

**Acceptance Scenarios**:

1. **Given** the local model service is running and at least one model is registered, **When** the operator follows the supported Open WebUI onboarding flow, **Then** the UI can connect to the local service and list the available model choices.
2. **Given** Open WebUI is connected to the local model service, **When** the operator sends a chat request through the UI, **Then** the request is completed through the existing local service without requiring the native macOS UI.

---

### User Story 2 - Understand the supported operator path (Priority: P2)

As a local model operator, I can see the current recommended workflow for interactive use so I do not waste time trying to launch or troubleshoot a surface that is no longer supported.

**Why this priority**: Replacing one UI with another only helps if the repository clearly communicates the new supported path and removes conflicting guidance.

**Independent Test**: Can be fully tested by reading the user-facing guidance from a clean checkout and verifying that it points operators to the local service plus Open WebUI flow instead of the native macOS shell.

**Acceptance Scenarios**:

1. **Given** a new operator opens the repository documentation, **When** they look for the recommended interactive UI workflow, **Then** they find a clear path that keeps the local model service and uses Open WebUI as the supported interface.
2. **Given** a new operator follows the repository guidance, **When** they review supported surfaces and prerequisites, **Then** they are not directed to build or launch the deleted native macOS UI.

---

### User Story 3 - Avoid broken migration states (Priority: P3)

As a local model operator, I can recover quickly when the service is unavailable or Open WebUI is pointed at the wrong address so the change in UI surface does not create confusing failures.

**Why this priority**: UI replacement can degrade the user experience if common connection failures are not handled by clear guidance.

**Independent Test**: Can be fully tested by attempting the supported workflow with the service stopped, with no registered models, and with an incorrect service address, then confirming the guidance explains how to correct each condition.

**Acceptance Scenarios**:

1. **Given** Open WebUI is configured before the local model service is started, **When** the operator attempts to use the UI, **Then** the supported guidance explains that the local service must be running first and shows the expected service address.
2. **Given** the operator points Open WebUI at an incorrect service address, **When** connection attempts fail, **Then** the supported guidance explains the expected address and how to verify it.

### Edge Cases

- What happens when the operator has no registered models after connecting Open WebUI to the local service?
- How does the system guide an operator who points Open WebUI somewhere other than `http://127.0.0.1:8000/v1`?
- What happens when the local model service is reachable but returns no selectable models because registrations are hidden or incomplete?
- How does the repository communicate the UI transition to an operator who still expects a native macOS shell?
- What happens when an operator tries to use an outdated UI launch command after the native shell has been removed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST keep the existing local serving workflow as the supported backend surface for interactive use.
- **FR-002**: The system MUST designate Open WebUI as the supported interactive UI for users who want a modern chat interface on top of the local service.
- **FR-003**: The system MUST provide a first-party onboarding path that tells operators how to connect Open WebUI to the local service at `http://127.0.0.1:8000/v1`.
- **FR-004**: The supported onboarding path MUST explain the minimum sequence required to succeed: start the local service, connect Open WebUI to the local endpoint, select an available model, and send a chat request.
- **FR-005**: The system MUST remove the native macOS UI from the set of supported operator surfaces so users are no longer directed to launch, build, or maintain it.
- **FR-006**: The repository’s user-facing guidance MUST clearly state that interactive chat use now flows through Open WebUI plus the local service rather than through a separate native shell, while legacy UI entry points behave only as migration notices.
- **FR-007**: The system MUST preserve the same model discovery and chat behavior through the local service so the UI migration does not require users to re-register models or change serving semantics.
- **FR-008**: The supported onboarding path MUST include recovery guidance for at least the following failure cases: local service not running, incorrect service address, and no registered models available for selection.
- **FR-009**: The system MUST ensure that any user-visible references to the retired native macOS UI are removed or rewritten to avoid conflicting instructions.

### Runtime, CLI & Observability Requirements

- **RCO-001**: This feature keeps `local-model serve` as the supported local service entry point and retires `local-model ui` as a supported operator workflow.
- **RCO-002**: The runtime path in scope remains the existing local serving path behind `local-model serve`; this feature does not introduce a new inference backend or change the established fallback behavior for optional runtime dependencies.
- **RCO-003**: This feature MUST not require new committed model artifacts or cache layout changes under `configs/`, `models/manifests/`, or `models/cache/`; any repository changes are limited to supported-surface assets such as documentation, scripts, and removal of retired UI assets.
- **RCO-004**: User-visible guidance MUST make it easy to diagnose whether a failure is caused by the local service being stopped, the endpoint being misconfigured, or no models being available.

### Key Entities *(include if feature involves data)*

- **Supported Operator Surface**: A user-facing way to interact with the local model system that the repository documents, maintains, and expects operators to rely on.
- **Open WebUI Onboarding Flow**: The first-party guidance that connects a user from a running local service to a working modern chat interface.
- **Local Service Endpoint**: The address the operator configures in Open WebUI to reach the existing local model service for model discovery and chat requests.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new operator can move from repository checkout to a successful Open WebUI chat round trip against the local service using only the documented supported workflow.
- **SC-002**: 100% of repository entry points that describe interactive UI usage point to the Open WebUI workflow and no longer instruct users to build or launch the retired native macOS UI.
- **SC-003**: Operators who already have registered models can complete the UI transition without re-registering models or changing the local service address from the documented endpoint.
- **SC-004**: In the three primary failure cases of service not running, incorrect service address, and no registered models, the supported guidance tells the operator how to identify and correct the problem.

## Assumptions

- Operators who want an interactive UI are willing to use a browser-based or web-hosted workspace rather than a bundled native macOS shell.
- The existing local model service remains the authoritative backend contract for model discovery and chat during this feature.
- The feature scope is limited to retiring the native shell and documenting a supported Open WebUI workflow, not redesigning the serving contract or adding new model capabilities.
- Existing registered models that are currently exposed through the local service remain sufficient for the initial Open WebUI workflow.
