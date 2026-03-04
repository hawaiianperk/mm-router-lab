from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RouterConfig:
    provider: str
    model: str
    endpoint: str
    api_key_env: str = "OPENAI_API_KEY"


def image_to_data_url(image_path: Path) -> str:
    raw = image_path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    suffix = image_path.suffix.lower().replace(".", "") or "png"
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    return f"data:image/{mime};base64,{b64}"


def build_payload(model: str, text_prompt: str, image_path: Path | None = None) -> dict[str, Any]:
    content: list[dict[str, Any]] = [{"type": "text", "text": text_prompt}]
    if image_path:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": image_to_data_url(image_path)},
            }
        )

    return {
        "model": model,
        "messages": [
            {"role": "user", "content": content},
        ],
        "temperature": 0.2,
    }


def invoke(config: RouterConfig, payload: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {"dry_run": True, "provider": config.provider, "payload": payload}

    api_key = os.getenv(config.api_key_env, "")
    if not api_key:
        raise RuntimeError(f"Environment variable '{config.api_key_env}' is required when dry_run is false")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url=config.endpoint, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        details = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Provider request failed: HTTP {e.code} - {details}") from e
