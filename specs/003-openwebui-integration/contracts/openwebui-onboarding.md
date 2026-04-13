# User Workflow Contract: Open WebUI Onboarding

## Supported Connection Path

- **Primary workflow**:
  1. Start the local service with `local-model serve`.
  2. Open Open WebUI in a browser.
  3. Add an OpenAI connection in the Open WebUI admin settings.
  4. Use `http://127.0.0.1:8000/v1` as the API URL when Open WebUI runs on the same host.

## Connection Settings

- **API URL**: `http://127.0.0.1:8000/v1`
- **API Key**: blank or placeholder token such as `none`
- **Model discovery**: expected to auto-detect from `/v1/models` when at least one registered model is visible
- **Verification commands**:
  - `curl http://127.0.0.1:8000/health`
  - `curl http://127.0.0.1:8000/v1/models`
  - `local-model list-models --json`

## Alternate Container Note

- If Open WebUI runs inside Docker while the local-model service runs on the host,
  the connection URL changes to `http://host.docker.internal:8000/v1`.

## Recovery Guidance

- If the connection fails because the service is unavailable, the operator must
  start or verify `local-model serve`.
- If no models appear, the operator must confirm that at least one registered
  model is returned from `/v1/models`.
- If the wrong endpoint is configured, the operator must correct it to the
  supported host-local URL shown above.
- If the operator still tries `local-model ui` or `./scripts/launch_ui.sh`, the command output is a migration notice only and the operator must continue the workflow in Open WebUI.
