from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_templates(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_template(templates: dict[str, Any], template_name: str, variables: dict[str, str]) -> str:
    if template_name not in templates:
        available = ", ".join(sorted(templates.keys()))
        raise KeyError(f"Template '{template_name}' not found. Available: {available}")

    prompt = str(templates[template_name]["prompt"])
    for key, value in variables.items():
        prompt = prompt.replace("{{" + key + "}}", value)
    return prompt
