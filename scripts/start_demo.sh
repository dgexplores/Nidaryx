#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing Python venv at .venv. Create it first, then rerun npm run demo." >&2
  exit 1
fi

cleanup() {
  if [[ -n "${API_PID:-}" ]]; then
    kill "$API_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

export PYTHONPATH="packages/contracts:packages/common-python:packages/telemetry-client:services/intelligence-core"
export VITE_NIDARYX_API_URL="${VITE_NIDARYX_API_URL:-http://127.0.0.1:8000}"

"$PYTHON_BIN" -m uvicorn app.main:app \
  --app-dir apps/api-gateway \
  --host 127.0.0.1 \
  --port 8000 &
API_PID=$!

echo "Nidaryx API: http://127.0.0.1:8000/docs"
echo "Nidaryx UI:  http://127.0.0.1:5173"
echo "Press Ctrl+C to stop both."

npm run web:dev
