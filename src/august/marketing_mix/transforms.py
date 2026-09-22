from __future__ import annotations

import numpy as np


def geometric_adstock(spend: np.ndarray, decay: float) -> np.ndarray:
    if not 0 <= decay < 1:
        raise ValueError("decay must be in [0, 1)")
    spend = np.asarray(spend, dtype=float)
    transformed = np.zeros_like(spend)

    for index, value in enumerate(spend):
        transformed[index] = value
        if index:
            transformed[index] += decay * transformed[index - 1]

    return transformed


def hill_saturation(
    exposure: np.ndarray,
    *,
    half_saturation: float,
    slope: float = 1.0,
) -> np.ndarray:
    if half_saturation <= 0 or slope <= 0:
        raise ValueError("half_saturation and slope must be positive")

    exposure = np.maximum(np.asarray(exposure, dtype=float), 0)
    numerator = np.power(exposure, slope)
    denominator = numerator + half_saturation**slope
    return np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0)
