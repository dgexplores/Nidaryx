#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="packages/contracts:packages/common-python:packages/telemetry-client:services/intelligence-core"
python3 -m unittest discover -s tests/unit -p "test_*.py"
docker compose config >/dev/null

