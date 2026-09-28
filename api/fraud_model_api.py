"""Standalone versioned inference for trusted, locally generated benchmark artifacts.

Run: AUGUST_FRAUD_ARTIFACTS=artifacts/fraud-real uvicorn api.fraud_model_api:app
"""
from __future__ import annotations

import json
import os
import time
from collections import deque
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from august.fraud.benchmark import FEATURES
from august.monitoring.drift import numeric_drift_report

app = FastAPI(title="AUGUST fraud research inference", version="0.1.0")
latencies_ms: deque[float] = deque(maxlen=1000)
counts = {"requests": 0, "errors": 0}


class PredictRequest(BaseModel):
    features: dict[str, float]


class DriftRequest(BaseModel):
    reference: list[float] = Field(min_length=2)
    current: list[float] = Field(min_length=2)


def _artifacts() -> tuple[object, dict]:
    root = Path(os.environ.get("AUGUST_FRAUD_ARTIFACTS", "artifacts/fraud-real"))
    model_path = root / "fraud-model.joblib"
    report_path = root / "fraud-report.json"
    if not model_path.is_file() or not report_path.is_file():
        raise HTTPException(status_code=503, detail="Train and register real model first")
    # joblib/pickle is executable: load ONLY artifacts created locally by a trusted operator.
    return joblib.load(model_path), json.loads(report_path.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": "research", "model_loaded": (
        Path(os.environ.get("AUGUST_FRAUD_ARTIFACTS", "artifacts/fraud-real")) /
        "fraud-model.joblib"
    ).is_file()}


@app.post("/v1/fraud/predict")
def predict(request: PredictRequest) -> dict:
    started = time.perf_counter()
    counts["requests"] += 1
    try:
        if set(request.features) != set(FEATURES) or not all(
            np.isfinite(value) for value in request.features.values()
        ):
            raise HTTPException(status_code=422, detail="Expected exactly 29 finite features")
        model, report = _artifacts()
        probability = float(model.predict_proba(
            pd.DataFrame([{k: request.features[k] for k in FEATURES}])
        )[0, 1])
        return {
            "fraud_probability": probability,
            "model": report["selected_model"],
            "dataset_sha256": report["dataset"]["dataframe_sha256"],
            "threshold": report["selected_threshold"],
            "flagged_for_review": probability >= report["selected_threshold"],
            "warning": "Research score only; not an operational fraud decision.",
        }
    except Exception:
        counts["errors"] += 1
        raise
    finally:
        latencies_ms.append((time.perf_counter() - started) * 1000)


@app.get("/v1/fraud/monitoring")
def monitoring() -> dict:
    return {"requests": counts["requests"], "errors": counts["errors"],
            "p95_latency_ms": float(np.percentile(latencies_ms, 95)) if latencies_ms else None,
            "window": "last_1000_in_process_requests",
            "predictive_quality": "unknown_without_delayed_ground_truth"}


@app.post("/v1/fraud/drift")
def drift(request: DriftRequest) -> dict:
    if not all(np.isfinite(x) for x in request.reference + request.current):
        raise HTTPException(status_code=422, detail="Values must be finite")
    return numeric_drift_report(np.array(request.reference), np.array(request.current))
