from __future__ import annotations

import pandas as pd


def difference_in_differences(
    data: pd.DataFrame,
    *,
    outcome: str,
    group: str,
    post: str,
) -> dict:
    required = {outcome, group, post}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    grouped = data.groupby([group, post], observed=True)[outcome].mean()

    control_pre = float(grouped.loc[(0, 0)])
    control_post = float(grouped.loc[(0, 1)])
    treatment_pre = float(grouped.loc[(1, 0)])
    treatment_post = float(grouped.loc[(1, 1)])

    control_change = control_post - control_pre
    treatment_change = treatment_post - treatment_pre

    return {
        "did_estimate": treatment_change - control_change,
        "control_change": control_change,
        "treatment_change": treatment_change,
        "identification_assumption": "Parallel trends absent treatment.",
        "warning": "The estimator alone does not validate parallel trends.",
    }
