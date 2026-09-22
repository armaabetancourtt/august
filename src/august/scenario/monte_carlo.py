from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ScenarioInputs:
    current_value_mxn: float
    annual_rent_mxn: float
    years: int = 5
    inflation_delta_pp: float = 0.0
    mortgage_rate_delta_pp: float = 0.0
    demand_delta_pct: float = 0.0
    supply_delta_pct: float = 0.0
    property_price_delta_pct: float = 0.0


def simulate_property_returns(
    inputs: ScenarioInputs,
    *,
    simulations: int = 10_000,
    seed: int = 42,
) -> dict:
    if inputs.current_value_mxn <= 0 or inputs.years <= 0:
        raise ValueError("current value and years must be positive")
    if simulations < 1_000:
        raise ValueError("use at least 1,000 simulations")

    rng = np.random.default_rng(seed)

    macro_drag = (
        -0.30 * (inputs.inflation_delta_pp / 100)
        -0.40 * (inputs.mortgage_rate_delta_pp / 100)
        + 0.12 * (inputs.demand_delta_pct / 100)
        - 0.10 * (inputs.supply_delta_pct / 100)
        + inputs.property_price_delta_pct / 100
    )

    appreciation = rng.normal(0.055 + macro_drag, 0.055, simulations)
    rent_growth = rng.normal(
        0.035 + 0.35 * inputs.demand_delta_pct / 100,
        0.025,
        simulations,
    )
    expense_ratio = np.clip(rng.normal(0.22, 0.05, simulations), 0.08, 0.45)

    terminal_value = inputs.current_value_mxn * np.power(1 + appreciation, inputs.years)
    total_net_rent = np.zeros(simulations)
    rent = np.full(simulations, inputs.annual_rent_mxn, dtype=float)

    for _ in range(inputs.years):
        total_net_rent += rent * (1 - expense_ratio)
        rent *= 1 + rent_growth

    final_value = terminal_value + total_net_rent
    total_return = final_value / inputs.current_value_mxn - 1
    downside = np.minimum(final_value - inputs.current_value_mxn, 0)

    return {
        "simulation_type": "conditional_monte_carlo",
        "simulations": simulations,
        "seed": seed,
        "expected_total_return_pct": round(float(np.mean(total_return) * 100), 2),
        "p10_total_return_pct": round(float(np.quantile(total_return, 0.10) * 100), 2),
        "p50_total_return_pct": round(float(np.quantile(total_return, 0.50) * 100), 2),
        "p90_total_return_pct": round(float(np.quantile(total_return, 0.90) * 100), 2),
        "probability_of_nominal_loss_pct": round(float(np.mean(total_return < 0) * 100), 2),
        "expected_downside_mxn": round(float(np.mean(downside)), 2),
        "warning": "Conditional simulation under explicit assumptions; not a certain forecast.",
    }
