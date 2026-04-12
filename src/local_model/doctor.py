from __future__ import annotations

import importlib.util
import platform
import sys
from pathlib import Path

from local_model.config import CACHE_DIR, CONFIG_DIR, FORKS_DIR, MANIFESTS_DIR
from local_model.models import DiagnosticCheck
from local_model.registry import list_manifests


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def collect_diagnostics() -> list[DiagnosticCheck]:
    checks = [
        DiagnosticCheck("python", "pass", f"Python {platform.python_version()}"),
        DiagnosticCheck("configs", "pass" if CONFIG_DIR.exists() else "fail", str(CONFIG_DIR)),
        DiagnosticCheck("cache_dir", "pass" if CACHE_DIR.exists() else "fail", str(CACHE_DIR)),
        DiagnosticCheck("manifests", "pass", f"{len(list_manifests())} registered manifest(s)"),
        DiagnosticCheck(
            "mlx_lm",
            "pass" if _module_available("mlx_lm") else "warn",
            "mlx_lm importable" if _module_available("mlx_lm") else "mlx_lm not installed",
        ),
        DiagnosticCheck(
            "fastapi",
            "pass" if _module_available("fastapi") else "warn",
            "fastapi importable" if _module_available("fastapi") else "fastapi not installed",
        ),
        DiagnosticCheck(
            "uvicorn",
            "pass" if _module_available("uvicorn") else "warn",
            "uvicorn importable" if _module_available("uvicorn") else "uvicorn not installed",
        ),
        DiagnosticCheck(
            "turbo_runtime",
            "pass" if _module_available("mlx_turboquant") else "warn",
            "mlx_turboquant importable"
            if _module_available("mlx_turboquant")
            else f"No importable turbo runtime; bridge placeholder at {FORKS_DIR / 'mlx_turboquant'}",
        ),
        DiagnosticCheck("platform", "pass" if sys.platform == "darwin" else "warn", sys.platform),
    ]
    return checks

