from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import urlopen


@dataclass(frozen=True)
class PrometheusQuery:
    expression: str
    timeout_seconds: int = 5


@dataclass(frozen=True)
class PrometheusSample:
    metric: dict[str, str]
    value: float
    timestamp: float


class TelemetryQueryError(RuntimeError):
    pass


class QueryClient(Protocol):
    def instant_query(self, query: PrometheusQuery) -> list[PrometheusSample]:
        ...


class PrometheusClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def instant_query(self, query: PrometheusQuery) -> list[PrometheusSample]:
        params = urlencode({"query": query.expression})
        url = f"{self.base_url}/api/v1/query?{params}"
        try:
            with urlopen(url, timeout=query.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - integration behavior
            raise TelemetryQueryError(f"prometheus query failed: {query.expression}") from exc

        if payload.get("status") != "success":
            raise TelemetryQueryError(payload.get("error", "prometheus query was not successful"))

        samples: list[PrometheusSample] = []
        for item in payload.get("data", {}).get("result", []):
            raw_timestamp, raw_value = item["value"]
            samples.append(
                PrometheusSample(
                    metric={str(k): str(v) for k, v in item.get("metric", {}).items()},
                    timestamp=float(raw_timestamp),
                    value=float(raw_value),
                )
            )
        return samples

