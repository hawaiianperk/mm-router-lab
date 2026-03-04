from __future__ import annotations

import argparse
import json
from pathlib import Path

from .router import RouterConfig, build_payload, invoke
from .templates import load_templates, render_template


def parse_vars(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --var format: {item}. Expected key=value")
        k, v = item.split("=", 1)
        out[k] = v
    return out


def render_cmd(args: argparse.Namespace) -> int:
    templates = load_templates(Path(args.templates))
    prompt = render_template(templates, args.template, parse_vars(args.var))
    print(prompt)
    return 0


def chat_cmd(args: argparse.Namespace) -> int:
    templates = load_templates(Path(args.templates))
    prompt = render_template(templates, args.template, parse_vars(args.var))

    cfg = RouterConfig(provider=args.provider, model=args.model, endpoint=args.endpoint, api_key_env=args.api_key_env)
    payload = build_payload(model=cfg.model, text_prompt=prompt, image_path=Path(args.image) if args.image else None)
    response = invoke(cfg, payload, dry_run=args.dry_run)

    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Unified request router for multimodal LLM APIs")
    sp = p.add_subparsers(dest="command", required=True)

    render = sp.add_parser("render", help="Render a prompt template")
    render.add_argument("--templates", required=True, help="Path to templates.json")
    render.add_argument("--template", required=True, help="Template name")
    render.add_argument("--var", action="append", default=[], help="Template variable key=value")
    render.set_defaults(func=render_cmd)

    chat = sp.add_parser("chat", help="Build request payload and optionally call provider")
    chat.add_argument("--provider", choices=["openai_compat", "ollama_compat"], default="openai_compat")
    chat.add_argument("--model", required=True)
    chat.add_argument("--endpoint", required=True, help="Chat completion endpoint URL")
    chat.add_argument("--templates", required=True)
    chat.add_argument("--template", required=True)
    chat.add_argument("--var", action="append", default=[])
    chat.add_argument("--image", default="", help="Optional local image path")
    chat.add_argument("--api-key-env", default="OPENAI_API_KEY")
    chat.add_argument("--dry-run", action="store_true")
    chat.set_defaults(func=chat_cmd)

    return p


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
