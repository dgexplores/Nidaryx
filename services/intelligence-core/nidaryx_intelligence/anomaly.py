from __future__ import annotations

from dataclasses import dataclass

from nidaryx_common.ids import stable_id
from nidaryx_contracts import (
    AnomalyEvent,
    ContributingFeature,
    FeatureVector,
    ModelMetadata,
    Severity,
    contract_hash,
)


@dataclass(frozen=True)
class BaselineProfile:
    means: dict[str, float]
    stddevs: dict[str, float]
    threshold: float
    model_version: str = "baseline-statistical.v1"
    preprocessing_version: str = "robust-zscore.v1"
    explanation_version: str = "top-zscore-contributors.v1"
    minimum_stddev: float = 1.0

    def z_score(self, name: str, value: float) -> float:
        mean = self.means.get(name, 0.0)
        stddev = max(abs(self.stddevs.get(name, self.minimum_stddev)), self.minimum_stddev)
        return (value - mean) / stddev


class BaselineDetector:
    def __init__(self, profile: BaselineProfile, max_contributors: int = 5) -> None:
        self.profile = profile
        self.max_contributors = max_contributors

    def score(self, vector: FeatureVector) -> AnomalyEvent:
        vector.validate()
        if not vector.data_quality.scoring_allowed:
            raise ValueError("data quality blocks anomaly scoring")

        scored_features: list[tuple[str, float, float]] = []
        for name, value in vector.values.items():
            scored_features.append((name, float(value), self.profile.z_score(name, float(value))))

        score = max((abs(z_score) for _, _, z_score in scored_features), default=0.0)
        contributors = tuple(
            ContributingFeature(
                name=name,
                value=value,
                baseline=self.profile.means.get(name, 0.0),
                deviation=abs(z_score),
                direction="above" if z_score >= 0 else "below",
            )
            for name, value, z_score in sorted(
                scored_features, key=lambda item: abs(item[2]), reverse=True
            )[: self.max_contributors]
        )
        severity = Severity.INFO
        if score >= self.profile.threshold * 1.5:
            severity = Severity.CRITICAL
        elif score >= self.profile.threshold:
            severity = Severity.WARNING

        model = ModelMetadata(
            model_version=self.profile.model_version,
            feature_schema_version=vector.schema_version,
            preprocessing_version=self.profile.preprocessing_version,
            threshold=self.profile.threshold,
            explanation_version=self.profile.explanation_version,
        )
        idempotency_key = stable_id(
            "anomkey",
            vector.entity,
            vector.window.started_at.isoformat(),
            vector.window.ended_at.isoformat(),
            vector.schema_version,
            contract_hash(vector.values),
        )
        return AnomalyEvent(
            id=stable_id("anom", idempotency_key),
            entity=vector.entity,
            detected_at=vector.window.ended_at,
            window=vector.window,
            score=round(score, 4),
            threshold=self.profile.threshold,
            severity=severity,
            contributing_features=contributors,
            data_quality=vector.data_quality,
            model=model,
            idempotency_key=idempotency_key,
            trace_ids=vector.trace_ids,
        )

