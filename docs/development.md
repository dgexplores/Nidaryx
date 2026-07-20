# Development Guide

## Setup

```bash
cp .env.example .env
python3 -m pip install -e ".[dev]"
npm install
```

## Local Checks

```bash
make test
make lint
make typecheck
npm --workspace apps/web-ui run typecheck
npm --workspace apps/web-ui run build
docker compose config
```

The core intelligence tests use the standard library `unittest` runner so they can run before pytest is installed.

## Engineering Rules

- Keep service boundaries explicit; shared domain behavior belongs in `services/intelligence-core`.
- Add tests with behavior changes.
- Do not weaken tests, suppress exceptions, or hide data-quality failures to force green status.
- Prefer deterministic fixtures for labelled fault scenarios and demo flows.
- Preserve safety gates around remediation and fault injection.

