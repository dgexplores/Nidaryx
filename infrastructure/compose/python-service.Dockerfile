FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/packages/contracts:/app/packages/common-python:/app/packages/telemetry-client:/app/services/intelligence-core

WORKDIR /app

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY services ./services
COPY apps ./apps
COPY runbooks ./runbooks

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -e .

EXPOSE 8080

CMD ["sh", "-c", "cd /app/${NIDARYX_SERVICE_DIR:-apps/api-gateway} && uvicorn app.main:app --host 0.0.0.0 --port 8080"]

