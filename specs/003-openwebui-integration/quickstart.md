# Quickstart: Replace macOS UI with Open WebUI

These smoke steps validate the supported interactive workflow after the native
macOS shell is retired.

## 1. Prepare the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
PYTHONPATH=src python -m local_model doctor
```

Expected outcome:

- `doctor` reports the local configuration and runtime prerequisites.
- The Python package is installed and ready to expose the local API.

## 2. Ensure at least one model is registered

If you already have a registered model, verify it:

```bash
PYTHONPATH=src python -m local_model list-models --json
```

If no model is registered yet, register an existing local model directory:

```bash
PYTHONPATH=src python -m local_model register demo \
  --path /path/to/model \
  --source-type local_dir \
  --source /path/to/model \
  --json
```

Expected outcome:

- `list-models` returns at least one alias that will be exposed through `/v1/models`.

## 3. Start the local API

```bash
PYTHONPATH=src python -m local_model serve --host 127.0.0.1 --port 8000
```

In another terminal, verify the service:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/models
```

Expected outcome:

- `/health` returns status `ok`.
- `/v1/models` returns at least one model card for a registered, API-visible model.

## 4. Start Open WebUI on the same machine

Use a native Open WebUI install so the documented local endpoint stays
`http://127.0.0.1:8000/v1`:

```bash
python -m pip install open-webui
open-webui serve
```

Then open the URL shown by Open WebUI in your browser.

Expected outcome:

- Open WebUI starts successfully on the local machine.
- You can reach the admin/settings interface from your browser.

## 5. Connect Open WebUI to the local-model service

In Open WebUI:

1. Go to `Admin Settings -> Connections -> OpenAI`.
2. Add a new connection.
3. Set the API URL to `http://127.0.0.1:8000/v1`.
4. Leave the API key empty or use a placeholder such as `none`.
5. Save the connection.

If Open WebUI is running in Docker instead of natively, replace the URL with
`http://host.docker.internal:8000/v1`.

Expected outcome:

- Open WebUI can query the local service and shows the registered model choices.

## 6. Send a chat request through Open WebUI

Choose one of the discovered models in Open WebUI and send a short prompt such
as:

`Reply with one short sentence confirming this request came through the local service.`

Expected outcome:

- The model responds through the local API.
- No native macOS UI is needed anywhere in the workflow.

## 7. Verify the retired command redirects operators

```bash
PYTHONPATH=src python -m local_model ui
```

Expected outcome:

- The command does not attempt to launch a native app.
- The output tells the operator to keep `local-model serve` running and connect Open WebUI to `http://127.0.0.1:8000/v1`.

## 8. Troubleshoot a stopped service

If Open WebUI cannot connect, verify the service first:

```bash
curl http://127.0.0.1:8000/health
```

Expected outcome:

- If the command fails, restart `local-model serve`.
- If the command succeeds, continue by checking `/v1/models`.

## 9. Troubleshoot missing or wrong models

If Open WebUI connects but shows no selectable models:

```bash
PYTHONPATH=src python -m local_model list-models --json
curl http://127.0.0.1:8000/v1/models
```

Expected outcome:

- `list-models --json` shows the registered aliases.
- `/v1/models` shows the API-visible model cards used by Open WebUI.
- If the API URL is wrong, correct it to `http://127.0.0.1:8000/v1` or `http://host.docker.internal:8000/v1` for Dockerized Open WebUI.

## 10. Validation notes

Validation recorded on 2026-04-12:

- `./.venv/bin/python -m pytest` passed with `23 passed`.
- `./.venv/bin/python -m local_model ui` printed the migration notice and exited with status `1`.
- `./scripts/launch_ui.sh` printed the shell migration helper and exited with status `1`.
- The Open WebUI browser onboarding remains the final operator smoke step because Open WebUI is installed and managed outside this repository.
