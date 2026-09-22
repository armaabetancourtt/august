from __future__ import annotations

from pathlib import Path

import pandas as pd

from august.analytics.executive import build_executive_overview
from august.synthetic.demo import generate_macro_history, generate_properties

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed" / "bi"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    macro = generate_macro_history()
    properties = generate_properties()
    overview = build_executive_overview(macro, properties)

    macro_export = macro.copy()
    macro_export["inflation_pct"] = macro_export["inflation"] * 100
    macro_export["policy_rate_pct"] = macro_export["policy_rate"] * 100
    macro_export = macro_export.drop(columns=["inflation", "policy_rate"])

    property_export = properties.copy()
    property_export["price_m2"] = property_export["price_mxn"] / property_export["area_m2"]

    neighborhood_export = pd.DataFrame(overview["neighborhoods"])
    kpi_export = pd.DataFrame(
        [
            {"metric": key, "value": value, "data_classification": "synthetic"}
            for key, value in overview["kpis"].items()
        ]
    )

    macro_export.to_csv(OUTPUT / "macro_monthly.csv", index=False)
    property_export.to_csv(OUTPUT / "property_fact.csv", index=False)
    neighborhood_export.to_csv(OUTPUT / "neighborhood_summary.csv", index=False)
    kpi_export.to_csv(OUTPUT / "executive_kpis.csv", index=False)

    print(f"BI exports written to {OUTPUT}")
    print("Use the CSVs directly in Power BI or Tableau; all rows are synthetic demo data.")


if __name__ == "__main__":
    main()
