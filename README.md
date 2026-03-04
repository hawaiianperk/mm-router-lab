# mm-router-lab

A compact routing layer for multimodal LLM APIs.

`mm-router-lab` helps you keep one request interface while switching providers/models.

## Features

- template-driven prompt rendering
- unified payload generation for text+image messages
- dry-run mode for debugging integration pipelines
- environment-variable based API key loading

## Why

When experimenting with VLMs, teams often switch between OpenAI-compatible endpoints, self-hosted serving, and local stacks. This project keeps integration code stable while changing only config.

## Install

```bash
pip install -e .
```

## Quick Start

Render a template:

```bash
cd mm-router-lab
PYTHONPATH=src python -m mm_router_lab.cli render \
  --templates examples/templates.json \
  --template caption_brief \
  --var audience="a data annotator"
```

Build payload in dry-run mode:

```bash
PYTHONPATH=src python -m mm_router_lab.cli chat \
  --provider openai_compat \
  --model qwen2.5-vl-7b-instruct \
  --endpoint https://api.openai.com/v1/chat/completions \
  --templates examples/templates.json \
  --template chart_qa \
  --var question="Is the trend increasing?" \
  --dry-run
```

## Notes

- For real calls, set API key env var (default `OPENAI_API_KEY`).
- `--image` accepts a local image path and auto-encodes as data URL.

## Roadmap

- add retry/backoff and structured error classes
- add provider-specific response extraction helpers
- add batch request mode with request tracing IDs

## License

MIT
