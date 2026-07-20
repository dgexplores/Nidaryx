from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceSettings:
    service_name: str
    environment: str
    log_level: str
    mongodb_uri: str
    prometheus_url: str
    grafana_url: str
    runbooks_path: str
    model_version: str
    feature_schema_version: str
    faults_enabled: bool

    @classmethod
    def from_env(cls, service_name: str | None = None) -> "ServiceSettings":
        return cls(
            service_name=service_name or os.getenv("TRACESENTRY_SERVICE_NAME", "tracesentry-service"),
            environment=os.getenv("TRACESENTRY_ENV", "development"),
            log_level=os.getenv("TRACESENTRY_LOG_LEVEL", "INFO"),
            mongodb_uri=os.getenv("TRACESENTRY_MONGODB_URI", "mongodb://localhost:27017/tracesentry"),
            prometheus_url=os.getenv("TRACESENTRY_PROMETHEUS_URL", "http://localhost:9090"),
            grafana_url=os.getenv("TRACESENTRY_GRAFANA_URL", "http://localhost:3000"),
            runbooks_path=os.getenv("TRACESENTRY_RUNBOOKS_PATH", "runbooks"),
            model_version=os.getenv("TRACESENTRY_MODEL_VERSION", "baseline-statistical.v1"),
            feature_schema_version=os.getenv(
                "TRACESENTRY_FEATURE_SCHEMA_VERSION", "feature-schema.v1"
            ),
            faults_enabled=os.getenv("TRACESENTRY_FAULTS_ENABLED", "false").lower() == "true",
        )

