from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path

from local_model.config import CACHE_DIR


class DownloadError(RuntimeError):
    pass


def ensure_cache_dir(alias: str) -> Path:
    destination = CACHE_DIR / alias
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def install_from_local_dir(alias: str, source: str, copy_files: bool = False) -> Path:
    src = Path(source).expanduser().resolve()
    if not src.exists() or not src.is_dir():
        raise DownloadError(f"Local directory does not exist: {source}")

    destination = CACHE_DIR / alias
    if destination.exists():
        if destination.is_symlink() or destination.is_file():
            destination.unlink()
        elif copy_files:
            shutil.rmtree(destination)

    if copy_files:
        shutil.copytree(src, destination, dirs_exist_ok=True)
    else:
        if destination.exists() and destination.is_dir():
            shutil.rmtree(destination)
        destination.symlink_to(src, target_is_directory=True)
    return destination


def install_from_direct_url(alias: str, source: str) -> Path:
    destination = ensure_cache_dir(alias)
    filename = source.rstrip("/").split("/")[-1] or "downloaded-model.bin"
    target = destination / filename
    urllib.request.urlretrieve(source, target)
    return destination


def install_from_hf_repo(alias: str, source: str) -> Path:
    destination = ensure_cache_dir(alias)
    try:
        from huggingface_hub import snapshot_download  # type: ignore
    except ImportError as exc:
        raise DownloadError(
            "huggingface_hub is not installed. Install it before using hf_repo sources."
        ) from exc

    snapshot_download(repo_id=source, local_dir=destination, local_dir_use_symlinks=False)
    return destination

