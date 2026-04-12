<!--
Sync Impact Report
Version change: unversioned template -> 1.0.0
Modified principles:
- Template Principle 1 -> I. Python Runtime Owns Execution
- Template Principle 2 -> II. One CLI Is the Public Control Plane
- Template Principle 3 -> III. Native UI Is an Orchestrator, Not a Second Runtime
- Template Principle 4 -> IV. Models Are Manifested, Cached, and Git-Safe
- Template Principle 5 -> V. Experimental Runtimes Must Be Adapter-Bound and Observable
Added sections:
- Platform and Repository Boundaries
- Delivery Workflow and Quality Gates
Removed sections:
- None
Templates requiring updates:
- ✅ updated: .specify/templates/plan-template.md
- ✅ updated: .specify/templates/spec-template.md
- ✅ updated: .specify/templates/tasks-template.md
- ✅ verified: no command templates present under .specify/templates/commands/
Follow-up TODOs:
- None
-->
# Local Model MLX Constitution

## Core Principles

### I. Python Runtime Owns Execution
All inference, downloads, benchmarking, model metadata resolution, and job control
MUST live in the Python runtime layer under repository-managed source. The macOS app,
helper scripts, and future integrations MUST call into this runtime or its CLI
entrypoints rather than reimplementing inference logic. Rationale: MLX and
TurboQuant experimentation remains debuggable only when there is one execution path.

### II. One CLI Is the Public Control Plane
Every user-facing workflow MUST be exposed through the `local-model` CLI with stable
subcommands and named presets. New capabilities MUST define command name,
arguments, expected stdout and stderr behavior, and any machine-readable output
before UI work begins. Rationale: the CLI is the shared contract across automation,
terminal use, and the macOS shell.

### III. Native UI Is an Orchestrator, Not a Second Runtime
The SwiftUI app MUST launch and observe the same runtime jobs and presets that
terminal users can invoke. UI-specific code MAY manage presentation, local state,
and interaction flow, but MUST NOT fork model loading, caching, or generation
semantics away from the runtime layer. Rationale: a macOS-first product stays
coherent when the UI is a shell over the same operational core.

### IV. Models Are Manifested, Cached, and Git-Safe
Committed artifacts MUST include only lightweight manifests, presets, and download
recipes; large weights MUST remain under `models/cache/` or another ignored cache
path. Every supported model MUST declare its alias, upstream source, runtime type,
local path convention, default preset, and machine-fit notes. Rationale: predictable
local model management is a core feature, while git history must remain small and
portable.

### V. Experimental Runtimes Must Be Adapter-Bound and Observable
Stock MLX functionality MUST remain operable before an experimental runtime ships.
Any TurboQuant or other experimental backend MUST sit behind a narrow adapter that
supports download, load, generate, stream, and benchmark flows, emits structured
logs and failure diagnostics, and records benchmark or health-check expectations
when behavior changes. Rationale: experimental speedups are valuable only when
failures stay isolated and diagnosable.

## Platform and Repository Boundaries

- Apple Silicon macOS is the primary supported environment until a later amendment
  explicitly broadens platform scope.
- Repository layout MUST preserve clear separation between runtime code in `src/`,
  committed metadata in `configs/` and `models/manifests/`, ignored weights in
  `models/cache/`, experimental backends in `forks/`, and the native shell in
  `apps/macos-ui/`.
- Scripts MAY automate bootstrap, download, or launch flows, but they MUST delegate
  substantive work to the runtime package or the `local-model` CLI.
- New runtime backends or model types MUST declare whether they affect stock MLX,
  experimental paths, or both, and MUST specify how the system degrades when
  optional dependencies are unavailable.
- Performance-sensitive work MUST define the primary metric it changes, such as
  startup latency, throughput, memory fit, or progress fidelity.

## Delivery Workflow and Quality Gates

- Every plan MUST pass a Constitution Check that identifies the runtime modules,
  CLI surface, UI orchestration boundary, model/cache impact, and observability
  strategy affected by the work.
- Every specification MUST document any new or changed command, preset,
  backend/runtime path, model manifest or cache behavior, failure mode, and
  user-visible progress or log output.
- Every task list MUST include the configuration, adapter or runner, integration,
  and validation work required to keep the runtime and UI paths aligned. Validation
  evidence MUST include doctor checks, benchmark capture, targeted automated tests,
  or other explicit verification appropriate to the change.
- Work MUST land in incremental slices that preserve a functioning stock MLX path
  before optional experimental integrations expand capability.
- Any justified deviation from these rules MUST be recorded in the plan's
  Complexity Tracking section before implementation begins.

## Governance

This constitution supersedes conflicting local practices for runtime architecture,
CLI design, model storage, and delivery gating.

Amendments MUST update this file, synchronize affected templates or guidance
documents, and record the scope of the change in the Sync Impact Report at the top
of the constitution.

Versioning policy for this constitution follows semantic versioning: MAJOR for
removing or redefining a principle or governance guarantee, MINOR for adding a
principle or materially expanding obligations, and PATCH for clarifications that do
not change required behavior.

Compliance review is mandatory at plan, specification, task-generation, and code
review time. Any unresolved deviation MUST be logged in the relevant Constitution
Check or Complexity Tracking section before implementation proceeds.

**Version**: 1.0.0 | **Ratified**: 2026-04-12 | **Last Amended**: 2026-04-12
