"""Reproducible, held-out benchmark on the real ULB/OpenML credit-card dataset.

No dataset is committed. Synthetic tests exercise the same split and training code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = [*(f"V{i}" for i in range(1, 29)), "Amount"]
REQUIRED = ["Time", *FEATURES, "Class"]
OPENML_DATA_ID = 1597
SEED = 42


def load_creditcard(*, csv: Path | None = None) -> tuple[pd.DataFrame, str]:
    """Explicit external-data source; fail rather than quietly substitute demo data."""
    if csv is None:
        from sklearn.datasets import fetch_openml

        frame = fetch_openml(data_id=OPENML_DATA_ID, as_frame=True).frame
        source = f"openml:{OPENML_DATA_ID}"
    else:
        raw = csv.read_bytes()
        frame = pd.read_csv(csv)
        source = f"local_csv_sha256:{hashlib.sha256(raw).hexdigest()}"
    missing = set(REQUIRED) - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
    frame = frame.loc[:, REQUIRED].copy()
    for col in REQUIRED:
        frame[col] = pd.to_numeric(frame[col], errors="raise")
    if frame.isna().any().any() or not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError("Dataset contains missing or non-finite values")
    if not frame["Class"].isin((0, 1)).all():
        raise ValueError("Class must contain only 0 and 1")
    if (frame["Amount"] < 0).any():
        raise ValueError("Amount must be non-negative")
    # Identical predictors may never straddle training/validation/test boundaries.
    frame = frame.sort_values("Time", kind="stable").drop_duplicates(
        subset=FEATURES, keep="first"
    ).reset_index(drop=True)
    if not frame["Time"].is_monotonic_increasing:
        raise ValueError("Time must support chronological splitting")
    return frame, source


def temporal_splits(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Chronological 60/20/20; no model, scaler or threshold sees the test labels."""
    ordered = frame.sort_values("Time", kind="stable").reset_index(drop=True)
    if ordered.duplicated(subset=FEATURES).any():
        raise ValueError("Identical feature rows could leak between splits")
    n = len(ordered)
    if n < 30:
        raise ValueError("At least 30 rows are required")
    train, validation, test = (
        ordered.iloc[: int(n * .6)],
        ordered.iloc[int(n * .6) : int(n * .8)],
        ordered.iloc[int(n * .8) :],
    )
    for name, part in (("train", train), ("validation", validation), ("test", test)):
        if part["Class"].nunique() != 2:
            raise ValueError(f"{name} must contain both classes for this benchmark")
    return train, validation, test


def _scores(labels: pd.Series, probabilities: np.ndarray, threshold: float) -> dict:
    y = labels.to_numpy(dtype=int)
    return {
        "rows": len(y),
        "fraud_count": int(y.sum()),
        "prevalence": float(y.mean()),
        "average_precision": float(average_precision_score(y, probabilities)),
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "brier_score": float(brier_score_loss(y, probabilities)),
        "precision_at_threshold": float(
            (y[probabilities >= threshold].mean()) if (probabilities >= threshold).any() else 0
        ),
        "recall_at_threshold": float(
            y[probabilities >= threshold].sum() / y.sum()
        ),
        "f1_at_threshold": float(f1_score(y, probabilities >= threshold, zero_division=0)),
        "threshold": float(threshold),
    }


def _validation_threshold(y: np.ndarray, probabilities: np.ndarray) -> float:
    candidates = np.r_[0.0, np.unique(np.quantile(probabilities, np.linspace(0, 1, 201)))]
    return float(max(candidates, key=lambda t: (
        f1_score(y, probabilities >= t, zero_division=0), -t
    )))


def run_benchmark(
    frame: pd.DataFrame,
    *,
    source: str,
    include_xgboost: bool = False,
) -> tuple[object, dict]:
    train, validation, test = temporal_splits(frame)
    candidates = {
        "prior_baseline": DummyClassifier(strategy="prior"),
        "logistic_regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(class_weight="balanced", max_iter=1000, random_state=SEED),
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, min_samples_leaf=3, class_weight="balanced_subsample",
            n_jobs=-1, random_state=SEED,
        ),
    }
    if include_xgboost:
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise RuntimeError("Install pip install -e '.[ml]' for XGBoost") from exc
        pos = int(train["Class"].sum())
        candidates["xgboost"] = XGBClassifier(
            n_estimators=150, max_depth=4, learning_rate=0.05, n_jobs=4,
            eval_metric="logloss", random_state=SEED,
            scale_pos_weight=(len(train) - pos) / pos,
        )
    validation_results = {}
    trained = {}
    for name, candidate in candidates.items():
        candidate.fit(train[FEATURES], train["Class"])
        proba = candidate.predict_proba(validation[FEATURES])[:, 1]
        threshold = _validation_threshold(validation["Class"].to_numpy(dtype=int), proba)
        validation_results[name] = _scores(validation["Class"], proba, threshold)
        trained[name] = candidate

    # Choose by validation average precision only; evaluate the untouched test once.
    selected = max(validation_results, key=lambda name: validation_results[name]["average_precision"])
    threshold = validation_results[selected]["threshold"]
    tests = {
        name: _scores(test["Class"], model.predict_proba(test[FEATURES])[:, 1],
                      validation_results[name]["threshold"])
        for name, model in trained.items()
    }
    dataset_hash = hashlib.sha256(
        pd.util.hash_pandas_object(frame[REQUIRED], index=False).values.tobytes()
    ).hexdigest()
    report = {
        "dataset": {"source": source, "openml_id": OPENML_DATA_ID,
                    "dataframe_sha256": dataset_hash, "rows_after_dedup": len(frame)},
        "split": "chronological_60_20_20_no_feature_duplicates",
        "features": FEATURES,
        "seed": SEED,
        "selection_metric": "validation_average_precision",
        "threshold_metric": "validation_f1",
        "selected_model": selected,
        "selected_threshold": threshold,
        "validation": validation_results,
        "test": tests,
        "limitations": [
            "Historical anonymized European-card data; not representative of production.",
            "No customer identifiers to establish a grouped user holdout.",
            "No live outcome labels, serving drift, financial impact or production SLA measured.",
        ],
    }
    return trained[selected], report


def save_artifacts(model: object, report: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output / "fraud-model.joblib")
    (output / "fraud-report.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
