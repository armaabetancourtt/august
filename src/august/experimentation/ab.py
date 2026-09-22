from __future__ import annotations

import math

from scipy.stats import norm


def required_sample_size_two_proportions(
    baseline_rate: float,
    minimum_detectable_effect: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    treatment_rate = baseline_rate + minimum_detectable_effect
    if not (0 < baseline_rate < 1 and 0 < treatment_rate < 1):
        raise ValueError("rates must lie in (0, 1)")

    p_bar = (baseline_rate + treatment_rate) / 2
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)

    numerator = (
        z_alpha * math.sqrt(2 * p_bar * (1 - p_bar))
        + z_beta
        * math.sqrt(
            baseline_rate * (1 - baseline_rate)
            + treatment_rate * (1 - treatment_rate)
        )
    ) ** 2

    return math.ceil(numerator / ((treatment_rate - baseline_rate) ** 2))


def analyze_two_proportion_experiment(
    control_conversions: int,
    control_total: int,
    treatment_conversions: int,
    treatment_total: int,
    *,
    alpha: float = 0.05,
) -> dict:
    p_c = control_conversions / control_total
    p_t = treatment_conversions / treatment_total
    diff = p_t - p_c
    pooled = (control_conversions + treatment_conversions) / (control_total + treatment_total)
    se_null = math.sqrt(pooled * (1 - pooled) * (1 / control_total + 1 / treatment_total))
    z = diff / se_null if se_null else 0.0
    p_value = 2 * (1 - norm.cdf(abs(z)))

    se_diff = math.sqrt(
        p_c * (1 - p_c) / control_total + p_t * (1 - p_t) / treatment_total
    )
    z_ci = norm.ppf(1 - alpha / 2)

    return {
        "control_rate": p_c,
        "treatment_rate": p_t,
        "absolute_effect": diff,
        "relative_lift": diff / p_c if p_c else None,
        "confidence_interval": (diff - z_ci * se_diff, diff + z_ci * se_diff),
        "p_value": p_value,
        "interpretation": "Estimate effect and uncertainty; do not reduce to winner/loser.",
    }
