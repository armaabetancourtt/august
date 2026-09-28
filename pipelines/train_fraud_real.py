"""Run: python -m pipelines.train_fraud_real [--csv data/raw/creditcard.csv]"""
from __future__ import annotations

import argparse
from pathlib import Path

from august.fraud.benchmark import load_creditcard, run_benchmark, save_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="ULB/OpenML fraud benchmark")
    parser.add_argument("--csv", type=Path, help="Local original ULB creditcard.csv; else OpenML 1597")
    parser.add_argument("--output", type=Path, default=Path("artifacts/fraud-real"))
    parser.add_argument("--xgboost", action="store_true", help="Optional [ml] dependency")
    args = parser.parse_args()
    frame, source = load_creditcard(csv=args.csv)
    model, report = run_benchmark(frame, source=source, include_xgboost=args.xgboost)
    save_artifacts(model, report, args.output)
    print("Selected model:", report["selected_model"])
    print("Validation AP:", report["validation"][report["selected_model"]]["average_precision"])
    print("Held-out test:", report["test"][report["selected_model"]])
    print("Report:", args.output / "fraud-report.json")


if __name__ == "__main__":
    main()
