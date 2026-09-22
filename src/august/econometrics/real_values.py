from __future__ import annotations


def inflation_adjusted_value(
    nominal_value: float,
    base_price_index: float,
    current_price_index: float,
) -> float:
    if nominal_value < 0:
        raise ValueError("nominal_value must be non-negative")
    if base_price_index <= 0 or current_price_index <= 0:
        raise ValueError("price indices must be positive")
    return nominal_value * (base_price_index / current_price_index)


def real_return(nominal_return: float, inflation_rate: float) -> float:
    if inflation_rate <= -1:
        raise ValueError("inflation_rate must be greater than -1")
    return ((1 + nominal_return) / (1 + inflation_rate)) - 1


def annualized_real_appreciation(
    initial_nominal: float,
    final_nominal: float,
    cumulative_inflation: float,
    years: float,
) -> float:
    if initial_nominal <= 0 or final_nominal <= 0 or years <= 0:
        raise ValueError("prices and years must be positive")
    real_growth = (final_nominal / initial_nominal) / (1 + cumulative_inflation)
    return real_growth ** (1 / years) - 1
