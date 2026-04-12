from __future__ import annotations

from pathlib import Path

from local_model.config import REPO_ROOT
from local_model.downloads import (
    DownloadError,
    install_from_direct_url,
    install_from_hf_repo,
    install_from_local_dir,
)
from local_model.models import ModelManifest
from local_model.registry import register_manifest


class InstallService:
    def install(
        self,
        *,
        alias: str,
        source_type: str,
        source: str,
        copy_files: bool = False,
        default_preset: str = "mlx-chat",
        turboquant_compatible: bool = False,
    ) -> ModelManifest:
        if source_type == "local_dir":
            destination = install_from_local_dir(alias, source, copy_files=copy_files)
        elif source_type == "direct_url":
            destination = install_from_direct_url(alias, source)
        elif source_type == "hf_repo":
            destination = install_from_hf_repo(alias, source)
        else:
            raise DownloadError(f"Unsupported source type: {source_type}")

        return register_manifest(
            alias=alias,
            source_type=source_type,
            source_location=source,
            local_path=str(Path(destination).resolve().relative_to(REPO_ROOT)),
            default_preset=default_preset,
            turboquant_compatible=turboquant_compatible,
        )

    def register(
        self,
        *,
        alias: str,
        source_type: str,
        source: str,
        local_path: str,
        default_preset: str = "mlx-chat",
        turboquant_compatible: bool = False,
        notes: str = "",
    ) -> ModelManifest:
        return register_manifest(
            alias=alias,
            source_type=source_type,
            source_location=source,
            local_path=local_path,
            default_preset=default_preset,
            turboquant_compatible=turboquant_compatible,
            notes=notes,
        )
