from __future__ import annotations

from pathlib import Path

from august.analytics.executive import build_executive_overview

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "GENERATED_EXECUTIVE_REPORT.md"


def main() -> None:
    overview = build_executive_overview()
    kpis = overview["kpis"]
    story = overview["story"]

    lines = [
        "# AUGUST — Executive Analytics Report",
        "",
        "> **SYNTHETIC DEMO DATA — NOT A REAL MARKET CLAIM**",
        "",
        f"**As of:** {overview['as_of']}",
        "",
        "## Executive readout",
        "",
        f"### {story['headline']}",
        "",
        f"**Signal.** {story['signal']}",
        "",
        f"**Evidence.** {story['evidence']}",
        "",
        f"**Why it matters.** {story['implication']}",
        "",
        f"**Next decision.** {story['next_decision']}",
        "",
        "## KPI snapshot",
        "",
        "| KPI | Value |",
        "|---|---:|",
        f"| Housing index, 12m change | {kpis['housing_change_12m_pct']:+.2f}% |",
        f"| Inflation, 12m change | {kpis['inflation_change_12m_pp']:+.2f} pp |",
        f"| Policy rate, 12m change | {kpis['policy_rate_change_12m_pp']:+.2f} pp |",
        f"| FX, 12m change | {kpis['fx_change_12m_pct']:+.2f}% |",
        f"| Median property price | MXN {kpis['median_property_price_mxn']:,.0f} |",
        f"| Median price / m² | MXN {kpis['median_price_m2']:,.0f} |",
        f"| Properties in demo | {kpis['property_count']} |",
        "",
        "## Neighborhood view",
        "",
        "| Neighborhood | Properties | Median MXN/m² | Median price |",
        "|---|---:|---:|---:|",
    ]

    for row in overview["neighborhoods"]:
        lines.append(
            f"| {row['neighborhood']} | {row['properties']} | "
            f"MXN {row['median_price_m2']:,.0f} | MXN {row['median_price_mxn']:,.0f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation guardrails",
            "",
            "- This report demonstrates analytics, BI and data storytelling workflows.",
            "- It does not represent observed market performance.",
            "- Correlation and directional movement are not presented as causal effects.",
            "- Re-run with python -m pipelines.generate_executive_report after changing demo data.",
            "",
        ]
    )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Executive report written to {REPORT}")


if __name__ == "__main__":
    main()
