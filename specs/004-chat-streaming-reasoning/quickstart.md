# Quickstart: Streaming Chat Completions with Reasoning Output

These smoke steps validate the new streamed chat behavior while preserving the
existing non-streaming contract.

## 1. Prepare the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install mlx-lm
PYTHONPATH=src python -m local_model doctor
```

Expected outcome:

- `doctor` reports the local runtime prerequisites.
- `mlx_lm` is available for the stock MLX runner.

## 2. Ensure at least one registered model is available

Verify the current manifest inventory:

```bash
PYTHONPATH=src python -m local_model list-models --json
```

Expected outcome:

- At least one API-visible alias is returned.
- Note one registered alias for steps 4 and 5.
- If a reasoning-capable manifest or preset is available for this feature branch, note that alias for step 6.

## 3. Start the local API

```bash
PYTHONPATH=src python -m local_model serve --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/models
```

Expected outcome:

- `/health` returns `status: ok`.
- `/v1/models` returns at least one registered model card.
- Reasoning-capable cards advertise `supports_streaming`, `reasoning_format`, and `reasoning_enabled_by_default`.

## 4. Verify the non-streaming chat contract still works

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{
    "model": "your-registered-alias",
    "messages": [{"role": "user", "content": "Reply with one short sentence."}]
  }'
```

Expected outcome:

- The response object remains `chat.completion`.
- `choices[0].message.content` contains the final assistant answer.
- If the selected model does not emit reasoning, `reasoning_content` is absent or empty.

## 5. Verify streamed chat output

```bash
curl -N -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{
    "model": "your-registered-alias",
    "stream": true,
    "messages": [{"role": "user", "content": "Count from one to five slowly."}]
  }'
```

Expected outcome:

- Multiple `data:` lines arrive before the full answer is complete.
- Each JSON payload is a `chat.completion.chunk`.
- The stream ends with `data: [DONE]`.

## 6. Verify reasoning-aware output with a supported configuration

Use a model alias or preset that actually emits reasoning text for this branch.
If the model family requires an instruction to enable reasoning, include that in
the prompt or system message for the smoke test.

```bash
curl -N -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{
    "model": "your-reasoning-alias",
    "preset": "mlx-api-reasoning",
    "stream": true,
    "messages": [
      {"role": "system", "content": "Think step by step if this model supports it."},
      {"role": "user", "content": "What is 17 multiplied by 19?"}
    ]
  }'
```

Expected outcome:

- Stream chunks include `delta.reasoning_content` only if the model actually emits reasoning.
- Final answer fragments remain separate from reasoning fragments.
- A matching non-stream request returns clean `message.content` and optional `message.reasoning_content`.
- The manifest or preset advertised by `/v1/models` matches the configuration used for the smoke test.

## 7. Verify unsupported streamed runtime behavior is explicit

If the selected runtime cannot stream incrementally, verify that the request
fails or falls back before generation starts instead of simulating a stream.

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{
    "model": "your-registered-alias",
    "stream": true,
    "runtime": "turboquant",
    "fallback_allowed": false,
    "messages": [{"role": "user", "content": "This should fail before generation."}]
  }'
```

Expected outcome:

- The request fails before any stream is emitted when the active runtime cannot satisfy real streaming.
- The error identifies the runtime limitation or incompatibility.

## 8. Suggested automated validation

Run targeted checks for the new behavior:

```bash
./.venv/bin/python -m pytest tests/contract tests/integration tests/unit
```

Expected outcome:

- Contract coverage validates streamed and non-streamed API responses.
- Unit coverage validates runner streaming and reasoning parsing boundaries.
- Integration coverage validates runtime fallback and end-to-end session behavior.
