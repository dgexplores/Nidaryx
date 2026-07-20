PYTHON ?= python3
PYTHONPATH := packages/contracts:packages/common-python:packages/telemetry-client:services/intelligence-core

.PHONY: help install test lint typecheck compose-config compose-up compose-down

help:
	@printf "TraceSentry commands:\\n"
	@printf "  make install         Install Python and web dependencies\\n"
	@printf "  make test            Run Python unit tests\\n"
	@printf "  make lint            Run Ruff lint/format checks\\n"
	@printf "  make typecheck       Run mypy\\n"
	@printf "  make compose-config  Validate Docker Compose configuration\\n"

install:
	$(PYTHON) -m pip install -e ".[dev]"
	npm install

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests/unit -p "test_*.py"

lint:
	ruff check .
	ruff format --check .

typecheck:
	mypy services packages

compose-config:
	docker compose config

compose-up:
	docker compose --profile demo up --build

compose-down:
	docker compose --profile demo down -v

