# Real-data fraud benchmark (research, not deployed)

**Implemented:** OpenML dataset ID [1597](https://www.openml.org/d/1597) / original ULB-Worldline anonymized transactions, explicit validation, chronological 60/20/20 split, deduplication by predictors before splitting, prior-only baseline, logistic regression and Random Forest, optional XGBoost, validation-only selection and F1 threshold tuning, held-out test metrics, versioned dataset fingerprint and trusted local model artifact. There are **no published performance numbers until this pipeline runs on the actual external dataset**.

## Reproduce

```bash
python -m pip install -e '.[dev]'
python -m pipelines.train_fraud_real --output artifacts/fraud-real
# Alternative: supply a downloaded original creditcard.csv
python -m pipelines.train_fraud_real --csv data/raw/creditcard.csv --xgboost
AUGUST_FRAUD_ARTIFACTS=artifacts/fraud-real uvicorn api.fraud_model_api:app
pytest tests/test_fraud_real_benchmark.py
```

The optional XGBoost candidate requires `pip install -e '.[ml,dev]'`. Downloaded data and trained artifacts remain local and excluded from source control. Review `artifacts/fraud-real/fraud-report.json` for data fingerprint, split, chosen model, validation and test results. The inference service accepts exactly the 29 features in `src/august/fraud/benchmark.py`; use `POST /v1/fraud/predict`. In-process request/error counts and p95 latency are at `GET /v1/fraud/monitoring`; `POST /v1/fraud/drift` computes numeric distribution drift on caller-supplied reference/current samples.

## Method and limits

The OpenML record is a *historical, anonymized* benchmark. The original `Time` field supports chronological partitioning, but it is **not** an input feature. All preprocessing is fitted only on training data. Models and their thresholds are compared exclusively on validation data, then scored once on held-out test data. Exact duplicate feature vectors are dropped; no customer IDs exist, so user-group leakage cannot be evaluated. Accuracy alone is unsuitable for extreme imbalance; compare average precision, ROC-AUC, Brier score, threshold precision/recall and F1. Scores are not monetary savings or evidence of real-world production performance.

This is separate from `pipelines/train_fraud_demo.py`, which is synthetic and remains explicitly labeled. No live traffic, delayed labels, drift alerts, or external production SLA are claimed. The inference service trusts locally produced joblib objects only: **never load an untrusted model file**. Additional security, live-label monitoring, run tracking and independent real-data executions remain future work.
