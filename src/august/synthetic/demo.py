from __future__ import annotations

import numpy as np
import pandas as pd


def generate_macro_history(*, periods: int = 72, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp("2026-08-01"), periods=periods, freq="MS")

    inflation = np.clip(0.045 + np.cumsum(rng.normal(0, 0.0015, periods)), 0.02, 0.09)
    policy_rate = np.clip(0.09 + np.cumsum(rng.normal(-0.00015, 0.0018, periods)), 0.04, 0.13)
    fx = np.clip(18.2 + np.cumsum(rng.normal(0, 0.12, periods)), 14, 25)
    activity = 100 + np.cumsum(rng.normal(0.18, 0.55, periods))
    housing_index = 100 * np.cumprod(1 + rng.normal(0.005, 0.008, periods))

    return pd.DataFrame(
        {
            "date": dates,
            "inflation": inflation,
            "policy_rate": policy_rate,
            "mxn_usd": fx,
            "economic_activity_index": activity,
            "housing_index": housing_index,
            "data_classification": "synthetic",
        }
    )


def generate_properties(*, rows: int = 400, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    neighborhoods = np.array(["North", "Central", "West", "South"])
    base_price = {"North": 42000, "Central": 51000, "West": 62000, "South": 47000}

    neighborhood = rng.choice(neighborhoods, size=rows, p=[0.24, 0.30, 0.28, 0.18])
    area = np.clip(rng.normal(125, 45, rows), 40, 350)
    bedrooms = np.clip(np.rint(area / 45 + rng.normal(0, 0.5, rows)), 1, 5).astype(int)
    bathrooms = np.clip(bedrooms - rng.choice([0, 0, 1], rows) + 0.5, 1, 4.5)
    ppm2 = np.array([base_price[n] for n in neighborhood], dtype=float)
    price = area * ppm2 * np.exp(rng.normal(0, 0.12, rows))

    return pd.DataFrame(
        {
            "property_id": [f"SYN-{i:05d}" for i in range(rows)],
            "city": "Synthetic Metro",
            "neighborhood": neighborhood,
            "area_m2": np.round(area, 1),
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "price_mxn": np.round(price, 0),
            "data_classification": "synthetic",
        }
    )
