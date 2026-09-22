from __future__ import annotations

from itertools import permutations


FACTORS = ("traffic", "conversion", "aov")


def revenue(traffic: float, conversion: float, aov: float) -> float:
    return traffic * conversion * aov


def shapley_revenue_decomposition(before: dict[str, float], after: dict[str, float]) -> dict:
    """Exact three-factor Shapley decomposition of a revenue change."""
    for factor in FACTORS:
        if factor not in before or factor not in after:
            raise ValueError(f"missing factor: {factor}")

    contributions = {factor: 0.0 for factor in FACTORS}
    orders = list(permutations(FACTORS))

    for order in orders:
        state = dict(before)
        previous_revenue = revenue(**state)

        for factor in order:
            state[factor] = after[factor]
            next_revenue = revenue(**state)
            contributions[factor] += next_revenue - previous_revenue
            previous_revenue = next_revenue

    for factor in contributions:
        contributions[factor] /= len(orders)

    total_change = revenue(**after) - revenue(**before)
    driver = max(contributions, key=lambda key: abs(contributions[key]))

    return {
        "before_revenue": revenue(**before),
        "after_revenue": revenue(**after),
        "total_change": total_change,
        "contributions": contributions,
        "largest_absolute_driver": driver,
        "method": "exact Shapley decomposition over traffic × conversion × AOV",
    }
