from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import joblib


@dataclass(frozen=True)
class ModelRecord:
    name: str
    version: str
    artifact_path: str
    dataset_version: str
    validation_strategy: str
    metrics: dict[str, float | None]
    created_at: str


def register_model(
    model: object,
    *,
    registry_dir: Path,
    name: str,
    version: str,
    dataset_version: str,
    validation_strategy: str,
    metrics: dict[str, float | None],
) -> ModelRecord:
    registry_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = registry_dir / f"{name}-{version}.joblib"
    metadata_path = registry_dir / f"{name}-{version}.json"

    joblib.dump(model, artifact_path)

    record = ModelRecord(
        name=name,
        version=version,
        artifact_path=str(artifact_path),
        dataset_version=dataset_version,
        validation_strategy=validation_strategy,
        metrics=metrics,
        created_at=datetime.now(UTC).isoformat(),
    )

    metadata_path.write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")
    return record
