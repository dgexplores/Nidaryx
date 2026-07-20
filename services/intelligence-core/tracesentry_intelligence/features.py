from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from tracesentry_contracts import DataQuality, DataQualityState, FeatureVector, TelemetryWindow


@dataclass(frozen=True)
class FeatureSchema:
    version: str
    required_features: tuple[str, ...]
    optional_features: tuple[str, ...] = ()

    def validate_values(self, values: dict[str, float]) -> None:
        missing = [name for name in self.required_features if name not in values]
        if missing:
            raise ValueError(f"missing required features: {', '.join(missing)}")


def evaluate_data_quality(
    *,
    missing_ratio: float,
    newest_sample_at: datetime,
    window_ended_at: datetime,
    max_staleness_seconds: int = 120,
    max_missing_ratio: float = 0.25,
) -> DataQuality:
    staleness = max(0.0, (window_ended_at - newest_sample_at).total_seconds())
    notes: list[str] = []
    state = DataQualityState.OK
    if missing_ratio > 0:
        notes.append(f"{missing_ratio:.0%} feature values missing")
        state = DataQualityState.PARTIAL
    if staleness > max_staleness_seconds:
        notes.append(f"newest sample is {staleness:.0f}s stale")
        state = DataQualityState.STALE
    if missing_ratio > max_missing_ratio:
        notes.append("missing ratio exceeds scoring gate")
        state = DataQualityState.BLOCKED
    return DataQuality(
        state=state,
        missing_ratio=missing_ratio,
        staleness_seconds=staleness,
        notes=tuple(notes),
    )


def build_feature_vector(
    *,
    entity: str,
    schema: FeatureSchema,
    window: TelemetryWindow,
    values: dict[str, float],
    data_quality: DataQuality,
    trace_ids: tuple[str, ...] = (),
    labels: dict[str, str] | None = None,
) -> FeatureVector:
    schema.validate_values(values)
    vector = FeatureVector(
        entity=entity,
        schema_version=schema.version,
        window=window,
        values=values,
        data_quality=data_quality,
        trace_ids=trace_ids,
        labels=labels or {},
    )
    vector.validate()
    return vector

