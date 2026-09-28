import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from august.fraud.benchmark import (
    FEATURES, load_creditcard, run_benchmark, save_artifacts, temporal_splits,
)


def fixture(n=300):
    rng = np.random.default_rng(42)
    frame = pd.DataFrame(rng.normal(size=(n, len(FEATURES))), columns=FEATURES)
    frame["Amount"] = rng.uniform(1, 100, n)
    frame["Time"] = np.arange(n)
    # Both classes in each chronological split; nontrivial signal.
    frame["Class"] = (np.arange(n) % 7 == 0).astype(int)
    return frame


def test_real_pipeline_holds_out_test_and_serializes(tmp_path):
    frame = fixture()
    train, val, test = temporal_splits(frame)
    assert train["Time"].max() < val["Time"].min() < test["Time"].min()
    model, report = run_benchmark(frame, source="test_fixture")
    assert report["selected_model"] in report["validation"]
    assert set(report["test"]) == {"prior_baseline", "logistic_regression", "random_forest"}
    assert report["test"][report["selected_model"]]["rows"] == len(test)
    save_artifacts(model, report, tmp_path)
    metadata = json.loads((tmp_path / "fraud-report.json").read_text())
    assert metadata["seed"] == 42
    assert metadata["environment"]["scikit_learn"]
    assert metadata["candidate_params"]
    assert metadata["model_artifact_sha256"] == hashlib.sha256(
        (tmp_path / "fraud-model.joblib").read_bytes()
    ).hexdigest()
    assert (tmp_path / "fraud-model.joblib").is_file()


def test_duplicate_predictors_rejected_to_prevent_leakage():
    frame = fixture()
    frame.loc[50, FEATURES] = frame.loc[5, FEATURES].values
    with pytest.raises(ValueError, match="leak"):
        temporal_splits(frame)


def test_loader_validates_and_deduplicates(tmp_path):
    frame = fixture(150)
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    csv = tmp_path / "creditcard.csv"
    frame.to_csv(csv, index=False)
    clean, source = load_creditcard(csv=csv)
    assert len(clean) == 150
    assert source.startswith("local_csv_sha256:")


def test_invalid_labels_fail(tmp_path):
    frame = fixture(150)
    frame.loc[0, "Class"] = 2
    csv = tmp_path / "bad.csv"
    frame.to_csv(csv, index=False)
    with pytest.raises(ValueError, match="Class"):
        load_creditcard(csv=csv)


def test_inference_verifies_model_fingerprint_and_rejects_tampering(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from api.fraud_model_api import _load_verified, app

    frame = fixture()
    model, report = run_benchmark(frame, source="test_fixture")
    save_artifacts(model, report, tmp_path)
    monkeypatch.setenv("AUGUST_FRAUD_ARTIFACTS", str(tmp_path))
    _load_verified.cache_clear()
    client = TestClient(app)
    features = {name: float(frame.iloc[0][name]) for name in FEATURES}
    ok = client.post("/v1/fraud/predict", json={"features": features})
    assert ok.status_code == 200
    assert 0 <= ok.json()["fraud_probability"] <= 1
    assert ok.json()["model_artifact_sha256"] == hashlib.sha256(
        (tmp_path / "fraud-model.joblib").read_bytes()
    ).hexdigest()

    (tmp_path / "fraud-model.joblib").write_bytes(b"tampered, do not deserialize")
    _load_verified.cache_clear()
    failed = client.post("/v1/fraud/predict", json={"features": features})
    assert failed.status_code == 503
    assert "fingerprint mismatch" in failed.json()["detail"]
