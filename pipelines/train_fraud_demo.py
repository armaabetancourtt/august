from __future__ import annotations

from pathlib import Path

from august.fraud.train import train_logistic_baseline
from august.mlops.registry import register_model
from august.synthetic.fraud import generate_fraud_transactions

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    frame = generate_fraud_transactions()
    result = train_logistic_baseline(frame)

    record = register_model(
        result["model"],
        registry_dir=ROOT / "artifacts" / "model_registry",
        name="fraud-logistic-baseline",
        version="0.1.0-synthetic",
        dataset_version="synthetic-fraud-v1-seed42",
        validation_strategy=result["metrics"]["split_strategy"],
        metrics={
            "pr_auc": result["metrics"]["pr_auc"],
            "roc_auc": result["metrics"]["roc_auc"],
            "brier_score": result["metrics"]["brier_score"],
        },
    )

    print("SYNTHETIC DATA benchmark completed.")
    print(result["metrics"])
    print(result["optimal_cost_threshold"])
    print(record)


if __name__ == "__main__":
    main()
