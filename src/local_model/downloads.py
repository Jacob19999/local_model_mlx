from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path

from local_model.config import CACHE_DIR
from local_model.registry import slugify


class DownloadError(RuntimeError):
    pass


def cache_destination_for_alias(alias: str) -> Path:
    return CACHE_DIR / slugify(alias)


def ensure_cache_dir(alias: str) -> Path:
    destination = cache_destination_for_alias(alias)
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def ensure_writable_destination(destination: Path) -> None:
    parent = destination if destination.exists() and destination.is_dir() else destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    probe = parent / ".local-model-write-test"
    try:
        probe.write_text("ok\n", encoding="utf-8")
    except OSError as exc:
        raise DownloadError(f"Cache destination is not writable: {destination}") from exc
    finally:
        probe.unlink(missing_ok=True)


def reset_destination(destination: Path) -> None:
    ensure_writable_destination(destination)
    if destination.is_symlink() or destination.is_file():
        destination.unlink()
    elif destination.is_dir():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)


def cleanup_destination(destination: Path) -> None:
    if destination.is_symlink() or destination.is_file():
        destination.unlink(missing_ok=True)
    elif destination.is_dir():
        shutil.rmtree(destination, ignore_errors=True)


def validate_artifact_set(destination: Path, source_type: str) -> None:
    if not destination.exists():
        raise DownloadError(f"Installed artifact set does not exist: {destination}")

    if source_type == "direct_url":
        if destination.is_dir() and not any(destination.iterdir()):
            raise DownloadError("Downloaded artifact set is empty.")
        return

    if not destination.is_dir():
        raise DownloadError(f"Installed artifact set is not a directory: {destination}")

    names = {path.name for path in destination.iterdir()}
    missing: list[str] = []
    if "config.json" not in names:
        missing.append("config.json")
    if not any(name in names for name in ("tokenizer.json", "tokenizer.model", "tokenizer_config.json")):
        missing.append("tokenizer metadata")

    has_weights = any(
        path.is_file()
        for pattern in ("*.safetensors", "*.safetensors.index.json", "*.bin", "*.gguf")
        for path in destination.glob(pattern)
    )
    if not has_weights:
        missing.append("model weights")

    if missing:
        raise DownloadError(
            "Installed artifacts are incomplete: missing " + ", ".join(missing) + f" in {destination}"
        )


def install_from_local_dir(alias: str, source: str, copy_files: bool = False) -> Path:
    src = Path(source).expanduser().resolve()
    if not src.exists() or not src.is_dir():
        raise DownloadError(f"Local directory does not exist: {source}")

    destination = cache_destination_for_alias(alias)
    ensure_writable_destination(destination)
    cleanup_destination(destination)

    if copy_files:
        shutil.copytree(src, destination)
    else:
        destination.symlink_to(src, target_is_directory=True)
    return destination


def install_from_direct_url(alias: str, source: str) -> Path:
    destination = cache_destination_for_alias(alias)
    reset_destination(destination)
    filename = source.rstrip("/").split("/")[-1] or "downloaded-model.bin"
    target = destination / filename
    try:
        urllib.request.urlretrieve(source, target)
    except Exception as exc:  # pragma: no cover - network failure surface
        raise DownloadError(f"Unable to download source URL `{source}`.") from exc
    return destination


def install_from_hf_repo(alias: str, source: str) -> Path:
    destination = cache_destination_for_alias(alias)
    reset_destination(destination)
    try:
        from huggingface_hub import snapshot_download  # type: ignore
    except ImportError as exc:
        raise DownloadError(
            "huggingface_hub is not installed. Install it before using hf_repo sources."
        ) from exc

    try:
        snapshot_download(repo_id=source, local_dir=destination, local_dir_use_symlinks=False)
    except Exception as exc:  # pragma: no cover - remote failure surface
        raise DownloadError(f"Unable to download Hugging Face repo `{source}`.") from exc
    return destination
