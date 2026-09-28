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
    assert json.loads((tmp_path / "fraud-report.json").read_text())["seed"] == 42
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
