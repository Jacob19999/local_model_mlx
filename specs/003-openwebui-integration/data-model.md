# Data Model: Replace macOS UI with Open WebUI

## Entity: Supported Operator Surface

- **Purpose**: Represents a user-facing interaction path that the repository documents and maintains.
- **Primary Fields**:
  - `name`: surface identifier, such as `cli`, `local-api`, or `openwebui`
  - `status`: `supported`, `deprecated`, or `removed`
  - `entrypoint`: command, URL, or document that starts the workflow
  - `depends_on_service`: whether the surface requires `local-model serve`
  - `notes`: operator-facing migration or usage guidance
- **Validation Rules**:
  - There must be exactly one supported interactive UI path after this feature: `openwebui`.
  - `local-api` remains supported and acts as the backend for the interactive UI path.
  - The retired native macOS shell must not remain in the `supported` set.

## Entity: Open WebUI Connection Profile

- **Purpose**: Captures the operator-provided settings that bind Open WebUI to the local service.
- **Primary Fields**:
  - `api_url`: expected default `http://127.0.0.1:8000/v1`
  - `api_key_mode`: blank or placeholder token such as `none`
  - `model_filter`: optional allowlist when manual model entry is needed
  - `service_state`: whether the local service is running and reachable
  - `model_visibility`: whether at least one registered model is returned for selection
- **Validation Rules**:
  - `api_url` must point at the local service’s OpenAI-compatible prefix.
  - `service_state` must be reachable before model discovery can succeed.
  - `model_visibility` depends on `/v1/models` returning at least one exposed model.

## Entity: UI Migration Notice

- **Purpose**: Represents the message shown to operators who try to use the retired native UI command.
- **Primary Fields**:
  - `invocation`: the legacy command the operator attempted, expected `local-model ui`
  - `status`: deprecation outcome
  - `replacement_workflow`: the supported next step, expected `local-model serve` plus Open WebUI connection guidance
  - `endpoint_hint`: expected endpoint string for the supported workflow
  - `exit_behavior`: whether the command returns a non-zero status after printing migration guidance
- **Validation Rules**:
  - The notice must mention the supported replacement workflow.
  - The notice must include the local service endpoint.
  - The notice must not imply that the native macOS UI still exists or can be launched.

## Relationships

- A **Supported Operator Surface** named `openwebui` depends on the **Open WebUI Connection Profile** to reach the local API.
- The **UI Migration Notice** exists only to redirect operators from the retired native UI surface to the supported `openwebui` surface.
- The local API remains the shared dependency for both the `cli` and `openwebui` supported surfaces.
