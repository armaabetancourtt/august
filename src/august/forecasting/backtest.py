from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np


ForecastFn = Callable[[np.ndarray, int], np.ndarray]


def naive_forecast(history: np.ndarray, horizon: int) -> np.ndarray:
    return np.repeat(history[-1], horizon)


def seasonal_naive_forecast(
    history: np.ndarray,
    horizon: int,
    season_length: int = 12,
) -> np.ndarray:
    if len(history) < season_length:
        return naive_forecast(history, horizon)
    season = history[-season_length:]
    return np.array([season[i % season_length] for i in range(horizon)], dtype=float)


def rolling_origin_backtest(
    values: Sequence[float],
    forecast_fn: ForecastFn,
    *,
    initial_window: int,
    horizon: int = 1,
    step: int = 1,
) -> dict:
    series = np.asarray(values, dtype=float)
    if initial_window < 3 or initial_window + horizon > len(series):
        raise ValueError("invalid backtest windows")

    errors = []
    abs_errors = []
    squared_errors = []
    mase_scores = []

    for origin in range(initial_window, len(series) - horizon + 1, step):
        train = series[:origin]
        actual = series[origin : origin + horizon]
        predicted = np.asarray(forecast_fn(train, horizon), dtype=float)
        if predicted.shape != actual.shape:
            raise ValueError("forecast_fn returned the wrong horizon")

        residual = actual - predicted
        errors.extend(residual.tolist())
        abs_errors.extend(np.abs(residual).tolist())
        squared_errors.extend(np.square(residual).tolist())

        scale = float(np.mean(np.abs(np.diff(train))))
        if scale > 0:
            mase_scores.append(float(np.mean(np.abs(residual)) / scale))

    return {
        "folds": len(mase_scores),
        "mae": float(np.mean(abs_errors)),
        "rmse": float(np.sqrt(np.mean(squared_errors))),
        "bias": float(np.mean(errors)),
        "mase": float(np.mean(mase_scores)) if mase_scores else None,
    }
