from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import expit


def generate_fraud_transactions(*, rows: int = 20_000, seed: int = 42) -> pd.DataFrame:
    """Generate explicitly synthetic, imbalanced transaction data."""
    rng = np.random.default_rng(seed)

    timestamps = pd.date_range("2025-01-01", periods=rows, freq="5min")
    amount = np.exp(rng.normal(5.8, 1.0, rows))
    account_age_days = np.clip(rng.gamma(4.0, 180.0, rows), 0, 4000)
    velocity_10m = rng.poisson(1.2, rows)
    device_changed = rng.binomial(1, 0.07, rows)
    distance_km = np.exp(rng.normal(2.0, 1.2, rows))
    refund_rate = rng.beta(1.2, 18.0, rows)
    night = ((timestamps.hour < 5) | (timestamps.hour > 23)).astype(int)

    logit = (
        -7.2
        + 0.0011 * np.maximum(amount - 1000, 0)
        + 0.55 * velocity_10m
        + 1.15 * device_changed
        + 0.003 * distance_km
        + 3.2 * refund_rate
        + 0.45 * night
        - 0.0004 * account_age_days
    )

    probability = np.clip(expit(logit), 0.0001, 0.995)
    fraud = rng.binomial(1, probability)

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "transaction_amount": amount,
            "account_age_days": account_age_days,
            "velocity_10m": velocity_10m,
            "device_changed": device_changed,
            "distance_km": distance_km,
            "refund_rate": refund_rate,
            "night": night,
            "fraud": fraud,
            "data_classification": "synthetic",
        }
    )
