from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from local_model.config import load_presets
from local_model.doctor import collect_diagnostics
from local_model.models import ExecutionRequest, GenerationResult
from local_model.registry import get_manifest, list_manifests
from local_model.runners.mlx_runner import MLXRunner
from local_model.runners.turbo_runner import TurboRunner
from local_model.services.diagnostics import render_manifest_summary, render_runtime_banner
from local_model.services.install_service import InstallService
from local_model.services.runtime_resolver import resolve_runtime

DEFAULT_UI_SERVICE_ROOT = "http://127.0.0.1:8000"
DEFAULT_OPENWEBUI_API_URL = f"{DEFAULT_UI_SERVICE_ROOT}/v1"
DOCKER_OPENWEBUI_API_URL = "http://host.docker.internal:8000/v1"
UI_MIGRATION_EXIT_CODE = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="local-model", description="Local MLX and TurboQuant control plane.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-models", help="List registered models.")
    list_parser.add_argument("--json", action="store_true")

    for name in ("run", "chat"):
        run_parser = subparsers.add_parser(name, help=f"{name.title()} with a registered model.")
        run_parser.add_argument("model_alias")
        run_parser.add_argument("--prompt")
        run_parser.add_argument("--preset", default=None)
        run_parser.add_argument("--runtime", choices=["mlx", "turboquant"], default=None)
        run_parser.add_argument("--no-fallback", action="store_true")
        run_parser.add_argument("--max-tokens", type=int, default=256)
        run_parser.add_argument("--temperature", type=float, default=0.7)
        run_parser.add_argument("--json", action="store_true")

    install_parser = subparsers.add_parser("install", help="Install and register a supported model.")
    install_parser.add_argument("alias")
    install_parser.add_argument("--source-type", choices=["hf_repo", "direct_url", "local_dir"], required=True)
    install_parser.add_argument("--source", required=True)
    install_parser.add_argument("--copy", action="store_true")
    install_parser.add_argument("--preset", default="mlx-chat")
    install_parser.add_argument("--turboquant-compatible", action="store_true")
    install_parser.add_argument("--json", action="store_true")

    register_parser = subparsers.add_parser("register", help="Register an existing local model path.")
    register_parser.add_argument("alias")
    register_parser.add_argument("--path", required=True)
    register_parser.add_argument("--source-type", default="local_dir")
    register_parser.add_argument("--source", required=True)
    register_parser.add_argument("--preset", default="mlx-chat")
    register_parser.add_argument("--turboquant-compatible", action="store_true")
    register_parser.add_argument("--notes", default="")
    register_parser.add_argument("--json", action="store_true")

    doctor_parser = subparsers.add_parser("doctor", help="Inspect local runtime prerequisites.")
    doctor_parser.add_argument("--json", action="store_true")

    serve_parser = subparsers.add_parser("serve", help="Launch the local OpenAI-compatible API.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    ui_parser = subparsers.add_parser("ui", help="Print migration guidance for the retired native UI command.")
    ui_parser.add_argument("--api-base-url", default=DEFAULT_UI_SERVICE_ROOT)

    return parser


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2))


def _read_prompt_from_stdin() -> str:
    if sys.stdin.isatty():
        return input("prompt> ").strip()
    return sys.stdin.read().strip()


def generate_once(
    *,
    model_alias: str,
    prompt: str,
    preset_name: str | None,
    requested_runtime: str | None,
    fallback_allowed: bool,
    source: str,
    max_tokens: int,
    temperature: float,
) -> GenerationResult:
    presets = load_presets()
    manifest = get_manifest(model_alias)
    preset = presets[preset_name or manifest.default_preset]
    decision = resolve_runtime(
        manifest=manifest,
        preset=preset,
        requested_runtime=requested_runtime,
        fallback_allowed=fallback_allowed,
    )
    request = ExecutionRequest(
        model_alias=model_alias,
        prompt=prompt,
        preset_name=preset.name,
        requested_runtime=decision.requested_runtime,
        fallback_allowed=fallback_allowed,
        source=source,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    runner = TurboRunner() if decision.active_runtime == "turboquant" else MLXRunner()
    return runner.generate(request=request, manifest=manifest, decision=decision)


def cmd_list_models(as_json: bool) -> int:
    manifests = [render_manifest_summary(item) for item in list_manifests()]
    if as_json:
        _print_json({"models": manifests})
        return 0
    if not manifests:
        print("No registered models. Use `local-model install` or `local-model register` first.")
        return 0
    for manifest in manifests:
        print(
            f"{manifest['alias']}: source={manifest['source_type']} "
            f"preset={manifest['default_preset']} runtimes={','.join(manifest['supported_runtimes'])}"
        )
    return 0


def cmd_run_chat(args: argparse.Namespace, source: str) -> int:
    prompt = args.prompt or _read_prompt_from_stdin()
    manifest = get_manifest(args.model_alias)
    preset_name = args.preset or manifest.default_preset
    preset = load_presets()[preset_name]
    decision = resolve_runtime(
        manifest=manifest,
        preset=preset,
        requested_runtime=args.runtime,
        fallback_allowed=not args.no_fallback,
    )
    for line in render_runtime_banner(manifest, decision):
        print(line)

    result = generate_once(
        model_alias=args.model_alias,
        prompt=prompt,
        preset_name=preset_name,
        requested_runtime=args.runtime,
        fallback_allowed=not args.no_fallback,
        source=source,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )
    if args.json:
        _print_json(result.to_dict())
    else:
        print(result.output_text)
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    manifest = InstallService().install(
        alias=args.alias,
        source_type=args.source_type,
        source=args.source,
        copy_files=args.copy,
        default_preset=args.preset,
        turboquant_compatible=args.turboquant_compatible,
    )
    payload = render_manifest_summary(manifest)
    if args.json:
        _print_json(payload)
    else:
        print(f"Installed and registered {manifest.alias} at {manifest.local_path}")
    return 0


def cmd_register(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    manifest = InstallService().register(
        alias=args.alias,
        source_type=args.source_type,
        source=args.source,
        local_path=str(path.relative_to(Path.cwd())) if path.is_relative_to(Path.cwd()) else str(path),
        default_preset=args.preset,
        turboquant_compatible=args.turboquant_compatible,
        notes=args.notes,
    )
    payload = render_manifest_summary(manifest)
    if args.json:
        _print_json(payload)
    else:
        print(f"Registered {manifest.alias} -> {manifest.local_path}")
    return 0


def cmd_doctor(as_json: bool) -> int:
    checks = [item.to_dict() for item in collect_diagnostics()]
    if as_json:
        _print_json({"checks": checks})
        return 0
    for item in checks:
        print(f"[{item['status']}] {item['name']}: {item['detail']}")
    return 0


def cmd_serve(host: str, port: int) -> int:
    try:
        import uvicorn
        from local_model.api.server import create_app
    except ImportError as exc:
        raise RuntimeError("FastAPI and uvicorn must be installed to use `local-model serve`.") from exc

    uvicorn.run(create_app(), host=host, port=port)
    return 0


def normalize_openwebui_api_url(api_base_url: str) -> str:
    normalized = api_base_url.rstrip("/")
    if normalized.endswith("/v1"):
        return normalized
    return f"{normalized}/v1"


def build_ui_migration_notice(api_base_url: str) -> list[str]:
    openwebui_api_url = normalize_openwebui_api_url(api_base_url)
    service_root = openwebui_api_url.removesuffix("/v1")
    return [
        "`local-model ui` has been retired. Use Open WebUI with the local service instead.",
        "",
        "Supported workflow:",
        f"1. Start the API: local-model serve --host 127.0.0.1 --port 8000",
        f"2. In Open WebUI, add an OpenAI-compatible connection to {openwebui_api_url}",
        "3. Leave the API key blank or use a placeholder such as `none`.",
        "4. Select a discovered model and send a test chat from Open WebUI.",
        "",
        "Recovery checks:",
        f"- Service unavailable: verify `curl {service_root}/health` returns `ok`.",
        f"- No models visible: verify `curl {openwebui_api_url}/models` and `local-model list-models --json`.",
        f"- Wrong endpoint: correct the Open WebUI connection URL to {openwebui_api_url}.",
        f"- Dockerized Open WebUI on the same host should use {DOCKER_OPENWEBUI_API_URL}.",
    ]


def cmd_ui(api_base_url: str) -> int:
    for line in build_ui_migration_notice(api_base_url):
        print(line)
    return UI_MIGRATION_EXIT_CODE


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "list-models":
            return cmd_list_models(args.json)
        if args.command == "run":
            return cmd_run_chat(args, source="cli-run")
        if args.command == "chat":
            return cmd_run_chat(args, source="cli-chat")
        if args.command == "install":
            return cmd_install(args)
        if args.command == "register":
            return cmd_register(args)
        if args.command == "doctor":
            return cmd_doctor(args.json)
        if args.command == "serve":
            return cmd_serve(args.host, args.port)
        if args.command == "ui":
            return cmd_ui(args.api_base_url)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1
