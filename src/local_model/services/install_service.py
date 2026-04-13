from __future__ import annotations

from pathlib import Path

from local_model.config import REPO_ROOT
from local_model.downloads import (
    DownloadError,
    cache_destination_for_alias,
    cleanup_destination,
    ensure_writable_destination,
    install_from_direct_url,
    install_from_hf_repo,
    install_from_local_dir,
    validate_artifact_set,
)
from local_model.models import InstallAttempt, ModelManifest
from local_model.registry import ensure_alias_available, register_manifest, resolve_install_source


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
        resolved_source = resolve_install_source(alias, source_type, source)
        destination = cache_destination_for_alias(alias)
        attempt = InstallAttempt(
            requested_alias=alias,
            source_type=resolved_source.type,
            source_location=resolved_source.location,
            destination_path=str(destination),
            copy_files=copy_files,
            default_preset=default_preset,
        )
        cleanup_on_failure = resolved_source.type != "local_dir" or copy_files

        ensure_alias_available(alias, resolved_source.type, resolved_source.location)
        ensure_writable_destination(destination)

        try:
            attempt.status = "fetching"
            if resolved_source.type == "local_dir":
                destination = install_from_local_dir(alias, resolved_source.location, copy_files=copy_files)
            elif resolved_source.type == "direct_url":
                destination = install_from_direct_url(alias, resolved_source.location)
            elif resolved_source.type == "hf_repo":
                destination = install_from_hf_repo(alias, resolved_source.location)
            else:
                raise DownloadError(f"Unsupported source type: {resolved_source.type}")

            attempt.status = "validating"
            validate_artifact_set(destination, resolved_source.type)

            manifest = register_manifest(
                alias=alias,
                source_type=resolved_source.type,
                source_location=resolved_source.location,
                local_path=str(Path(destination).relative_to(REPO_ROOT)),
                default_preset=default_preset,
                turboquant_compatible=turboquant_compatible,
            )
            attempt.status = "registered"
            return manifest
        except Exception as exc:
            attempt.status = "failed"
            attempt.error_reason = str(exc)
            if cleanup_on_failure:
                cleanup_destination(destination)
            raise

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
        resolved_path = Path(local_path).expanduser().resolve()
        validate_artifact_set(resolved_path, source_type)
        return register_manifest(
            alias=alias,
            source_type=source_type,
            source_location=source,
            local_path=str(resolved_path.relative_to(REPO_ROOT)) if resolved_path.is_relative_to(REPO_ROOT) else str(resolved_path),
            default_preset=default_preset,
            turboquant_compatible=turboquant_compatible,
            notes=notes,
        )
