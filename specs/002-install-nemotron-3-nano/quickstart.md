# Quickstart: Install Nemotron 3 Nano 30B A3B

These smoke steps validate the model-onboarding path without introducing a new
command family.

## 1. Prepare the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install huggingface_hub mlx-lm
PYTHONPATH=src python -m local_model doctor
```

Expected outcome:

- `doctor` reports the config and cache directories.
- `mlx_lm` is visible.
- `huggingface_hub` is available for `hf_repo` installs.

## 2. Install the recommended MLX source

```bash
PYTHONPATH=src python -m local_model install nemotron-3-nano-30b-a3b \
  --source-type hf_repo \
  --source lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit \
  --json
```

Expected outcome:

- The command returns manifest JSON for alias `nemotron-3-nano-30b-a3b`.
- The install writes a cache directory under `models/cache/nemotron-3-nano-30b-a3b/`.
- A manifest file is created under `models/manifests/nemotron-3-nano-30b-a3b.yaml`.

## 2a. Verify alias conflicts are non-destructive

```bash
PYTHONPATH=src python -m local_model install nemotron-3-nano-30b-a3b \
  --source-type hf_repo \
  --source some-other-owner/conflicting-repo
```

Expected outcome:

- The command exits non-zero with `error: Alias ... already maps to ...`.
- The existing Nemotron manifest remains unchanged.
- No new manifest is written over the existing registration.

## 3. Confirm discovery

```bash
PYTHONPATH=src python -m local_model list-models --json
```

Expected outcome:

- The installed Nemotron alias appears in the returned model list.
- The entry shows source type `hf_repo` and default runtime `mlx`.

## 4. Run the installed model through stock MLX

```bash
PYTHONPATH=src python -m local_model run nemotron-3-nano-30b-a3b \
  --prompt "Reply with one short sentence proving the model loaded." \
  --json
```

Expected outcome:

- The runtime banner reports `requested_runtime: mlx` and `active_runtime: mlx`.
- The command returns a non-empty completion payload.

## 4a. Verify interrupted or incomplete installs do not register

Simulate an interrupted snapshot by removing a required file from the cache
before validation completes, or by pointing the install flow at a test fixture
that omits tokenizer metadata.

Expected outcome:

- The command exits non-zero with an incomplete-artifact error.
- `models/manifests/nemotron-3-nano-30b-a3b.yaml` is not created for the failed attempt.
- Temporary cache contents created by the failed remote install are cleaned up.

## 5. Verify unsupported runtime behavior is explicit

```bash
PYTHONPATH=src python -m local_model run nemotron-3-nano-30b-a3b \
  --runtime turboquant \
  --no-fallback \
  --prompt "This should fail before generation."
```

Expected outcome:

- The command exits non-zero before generation starts.
- The error explains that the manifest is not TurboQuant-compatible unless that metadata is intentionally added later.

## 5a. Verify insufficient cache permissions are explicit

Make the target cache directory unwritable and re-run the install:

```bash
chmod -w models/cache
PYTHONPATH=src python -m local_model install nemotron-3-nano-30b-a3b \
  --source-type hf_repo \
  --source lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-4bit
chmod +w models/cache
```

Expected outcome:

- The command exits non-zero before registration.
- The error identifies the cache destination as not writable.
- No manifest entry is created for the failed install.

## 6. Optional API discovery check

```bash
PYTHONPATH=src python -m local_model serve --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/v1/models
```

Expected outcome:

- `/v1/models` includes `nemotron-3-nano-30b-a3b` when `api_visible` remains true.
