from __future__ import annotations

from typing import Any

import pandas as pd

from august.synthetic.demo import generate_macro_history, generate_properties


def _direction(value: float, *, tolerance: float = 0.10) -> str:
    if value > tolerance:
        return "up"
    if value < -tolerance:
        return "down"
    return "flat"


def build_executive_overview(
    macro: pd.DataFrame | None = None,
    properties: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Build a BI-friendly executive view from AUGUST demo data.

    The function deliberately separates computed evidence from narrative.
    Default inputs are deterministic synthetic data and are labelled as such.
    """
    macro = generate_macro_history() if macro is None else macro.copy()
    properties = generate_properties() if properties is None else properties.copy()

    if len(macro) < 13:
        raise ValueError("Executive overview requires at least 13 monthly observations.")
    if properties.empty:
        raise ValueError("Executive overview requires at least one property.")

    macro = macro.sort_values("date").reset_index(drop=True)
    latest = macro.iloc[-1]
    year_ago = macro.iloc[-13]

    housing_change = (float(latest["housing_index"]) / float(year_ago["housing_index"]) - 1) * 100
    inflation_change = (float(latest["inflation"]) - float(year_ago["inflation"])) * 100
    policy_change = (float(latest["policy_rate"]) - float(year_ago["policy_rate"])) * 100
    fx_change = (float(latest["mxn_usd"]) / float(year_ago["mxn_usd"]) - 1) * 100

    properties["price_m2"] = properties["price_mxn"] / properties["area_m2"]
    neighborhood = (
        properties.groupby("neighborhood", as_index=False)
        .agg(
            properties=("property_id", "count"),
            median_price_mxn=("price_mxn", "median"),
            median_price_m2=("price_m2", "median"),
            median_area_m2=("area_m2", "median"),
        )
        .sort_values("median_price_m2", ascending=False)
        .reset_index(drop=True)
    )

    top_market = neighborhood.iloc[0]
    housing_direction = _direction(housing_change, tolerance=0.5)
    inflation_direction = _direction(inflation_change)
    policy_direction = _direction(policy_change)

    housing_phrase = {"up": "rose", "down": "fell", "flat": "was broadly flat"}[
        housing_direction
    ]
    inflation_phrase = {
        "up": "accelerated",
        "down": "eased",
        "flat": "was broadly unchanged",
    }[inflation_direction]

    headline = (
        f"Synthetic housing index {housing_phrase} {abs(housing_change):.1f}% YoY "
        f"while inflation {inflation_phrase} {abs(inflation_change):.2f} pp."
    )

    story = {
        "headline": headline,
        "signal": (
            f"Pricing momentum is {housing_direction}; inflation is {inflation_direction}; "
            f"the policy-rate signal is {policy_direction}."
        ),
        "evidence": (
            f"The housing index changed {housing_change:+.1f}% over 12 months, inflation moved "
            f"{inflation_change:+.2f} pp, and the policy rate moved {policy_change:+.2f} pp. "
            f"{top_market['neighborhood']} has the highest demo median price per m² at "
            f"MXN {float(top_market['median_price_m2']):,.0f}."
        ),
        "implication": (
            "Nominal price momentum alone is not enough for an investment decision. "
            "AUGUST separates market movement from inflation, financing pressure and "
            "neighborhood-level pricing before surfacing a recommendation."
        ),
        "next_decision": (
            "Prioritize neighborhood-level underwriting and stress-test financing and "
            "real-return downside before treating appreciation as durable value creation."
        ),
    }

    series = []
    for _, row in macro.tail(24).iterrows():
        series.append(
            {
                "date": pd.Timestamp(row["date"]).strftime("%Y-%m"),
                "inflation_pct": round(float(row["inflation"]) * 100, 2),
                "policy_rate_pct": round(float(row["policy_rate"]) * 100, 2),
                "mxn_usd": round(float(row["mxn_usd"]), 2),
                "economic_activity_index": round(float(row["economic_activity_index"]), 2),
                "housing_index": round(float(row["housing_index"]), 2),
            }
        )

    neighborhoods = [
        {
            "neighborhood": str(row["neighborhood"]),
            "properties": int(row["properties"]),
            "median_price_mxn": round(float(row["median_price_mxn"]), 0),
            "median_price_m2": round(float(row["median_price_m2"]), 0),
            "median_area_m2": round(float(row["median_area_m2"]), 1),
        }
        for _, row in neighborhood.iterrows()
    ]

    return {
        "market": "SYNTHETIC METRO",
        "data_classification": "synthetic",
        "as_of": str(pd.Timestamp(latest["date"]).date()),
        "kpis": {
            "housing_change_12m_pct": round(housing_change, 2),
            "inflation_change_12m_pp": round(inflation_change, 2),
            "policy_rate_change_12m_pp": round(policy_change, 2),
            "fx_change_12m_pct": round(fx_change, 2),
            "median_property_price_mxn": round(float(properties["price_mxn"].median()), 0),
            "median_price_m2": round(float(properties["price_m2"].median()), 0),
            "property_count": int(len(properties)),
        },
        "story": story,
        "market_series": series,
        "neighborhoods": neighborhoods,
        "bi_contract": {
            "grain_macro": "one row per month",
            "grain_properties": "one row per property",
            "dimensions": ["date", "neighborhood", "city", "data_classification"],
            "measures": [
                "housing_index",
                "inflation_pct",
                "policy_rate_pct",
                "price_m2",
                "median_price_mxn",
            ],
        },
        "warning": "Synthetic demo data. Not an observation about Mexico or any real market.",
    }
