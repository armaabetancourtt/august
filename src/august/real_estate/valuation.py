from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from august.core.contracts import DataClassification, Evidence, Provenance
from august.econometrics.real_values import real_return


@dataclass(frozen=True)
class PropertyFeatures:
    city: str
    neighborhood: str
    asking_price_mxn: float
    area_m2: float
    bedrooms: int
    bathrooms: float


@dataclass(frozen=True)
class MarketContext:
    neighborhood_price_m2: float
    annual_inflation: float
    mortgage_rate: float
    rental_yield: float
    demand_index: float
    supply_index: float


def analyze_property(
    property_: PropertyFeatures,
    market: MarketContext,
    *,
    data_classification: DataClassification = DataClassification.SYNTHETIC,
) -> dict:
    if property_.asking_price_mxn <= 0 or property_.area_m2 <= 0:
        raise ValueError("price and area must be positive")
    if market.neighborhood_price_m2 <= 0:
        raise ValueError("neighborhood_price_m2 must be positive")

    size_component = property_.area_m2 * market.neighborhood_price_m2
    bedroom_adjustment = min(property_.bedrooms, 5) * 0.012
    bathroom_adjustment = min(property_.bathrooms, 5) * 0.009
    demand_adjustment = 0.08 * (market.demand_index - 1.0)
    supply_adjustment = -0.07 * (market.supply_index - 1.0)
    rate_pressure = -0.45 * max(0.0, market.mortgage_rate - 0.08)
    inflation_pressure = -0.10 * max(0.0, market.annual_inflation - 0.04)

    multiplier = (
        1.0
        + bedroom_adjustment
        + bathroom_adjustment
        + demand_adjustment
        + supply_adjustment
        + rate_pressure
        + inflation_pressure
    )

    fair_value = max(
        size_component * multiplier,
        property_.area_m2 * market.neighborhood_price_m2 * 0.65,
    )
    asking_gap = property_.asking_price_mxn / fair_value - 1
    expected_monthly_rent = fair_value * market.rental_yield / 12
    real_rental_yield = real_return(market.rental_yield, market.annual_inflation)
    affordability_pressure_pp = max(market.mortgage_rate - 0.08, 0.0) * 100

    relative_uncertainty = 0.12 + 0.05 * abs(market.demand_index - market.supply_index)
    lower = fair_value * (1 - relative_uncertainty)
    upper = fair_value * (1 + relative_uncertainty)
    confidence = float(np.clip(1 - relative_uncertainty, 0.55, 0.92))

    if asking_gap > 0.10:
        decision = "PRICE ABOVE BASELINE FAIR-VALUE RANGE"
    elif asking_gap < -0.10:
        decision = "PRICE BELOW BASELINE FAIR-VALUE RANGE"
    else:
        decision = "PRICE NEAR BASELINE FAIR VALUE"

    evidence = [
        Evidence(
            label="size × neighborhood baseline",
            value=round(size_component, 2),
            direction="base",
            method="area_m2 × neighborhood_price_m2",
            confidence=confidence,
        ),
        Evidence(
            label="demand adjustment",
            value=round(demand_adjustment * fair_value, 2),
            direction="up" if demand_adjustment >= 0 else "down",
            method="transparent baseline coefficient",
            confidence=confidence,
        ),
        Evidence(
            label="supply adjustment",
            value=round(supply_adjustment * fair_value, 2),
            direction="up" if supply_adjustment >= 0 else "down",
            method="transparent baseline coefficient",
            confidence=confidence,
        ),
        Evidence(
            label="interest-rate pressure",
            value=round(rate_pressure * fair_value, 2),
            direction="down" if rate_pressure < 0 else "neutral",
            method="transparent baseline coefficient",
            confidence=confidence,
        ),
    ]

    return {
        "decision": decision,
        "fair_value_mxn": round(fair_value, 2),
        "fair_value_interval_95_like": [round(lower, 2), round(upper, 2)],
        "asking_price_mxn": round(property_.asking_price_mxn, 2),
        "asking_gap_pct": round(asking_gap * 100, 2),
        "expected_monthly_rent_mxn": round(expected_monthly_rent, 2),
        "nominal_rental_yield_pct": round(market.rental_yield * 100, 2),
        "real_rental_yield_pct": round(real_rental_yield * 100, 2),
        "interest_rate_affordability_pressure_pp": round(affordability_pressure_pp, 2),
        "confidence": round(confidence, 3),
        "evidence": [item.model_dump() for item in evidence],
        "assumptions": [
            "Baseline coefficients are engineering assumptions, not fitted production coefficients.",
            "Neighborhood price per square meter is the primary comparable anchor.",
            "The interval is a scenario uncertainty band, not a calibrated prediction interval yet.",
            "Real rental yield uses the current inflation assumption via the Fisher relation.",
        ],
        "limitations": [
            "No fitted comparable-sales model is included in the foundation milestone.",
            "Building age, amenities, floor, parking and exact geospatial features are not yet modeled.",
        ],
        "provenance": [
            Provenance(
                classification=data_classification,
                source="AUGUST demo market context",
                generated_by="src/august/real_estate/valuation.py",
                notes=["Synthetic unless a real public-data pipeline is explicitly selected."],
            ).model_dump()
        ],
    }
