#!/usr/bin/env bash
set -euo pipefail

api_base_url="${LOCAL_MODEL_API_BASE_URL:-http://127.0.0.1:8000}"
api_base_url="${api_base_url%/}"

if [[ "${api_base_url}" == */v1 ]]; then
  openwebui_api_url="${api_base_url}"
  service_root="${api_base_url%/v1}"
else
  openwebui_api_url="${api_base_url}/v1"
  service_root="${api_base_url}"
fi

cat <<EOF
\`./scripts/launch_ui.sh\` no longer launches the retired macOS UI.

Supported workflow:
1. Start the API: local-model serve --host 127.0.0.1 --port 8000
2. In Open WebUI, add an OpenAI-compatible connection to ${openwebui_api_url}
3. Leave the API key blank or use \`none\`
4. Verify the service with:
   curl ${service_root}/health
   curl ${openwebui_api_url}/models

If Open WebUI runs in Docker on the same host, use:
  http://host.docker.internal:8000/v1
EOF

exit 1
