"""Bounded AUGUST analytical agent: only allowlisted, deterministic local tools.

The LLM never chooses arbitrary Python/SQL or edits a tool result. All outputs in
the primary answer are computed before optional generation; optional quote checks
prove only that cited text exists, not the semantic truth of model prose.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from august.core.contracts import DataClassification
from august.llm.grounded import answer_with_quotes
from august.real_estate.valuation import MarketContext, PropertyFeatures, analyze_property
from august.scenario.monte_carlo import ScenarioInputs, simulate_property_returns


SHOCK_FIELDS = (
    "inflation_delta_pp",
    "mortgage_rate_delta_pp",
    "demand_delta_pct",
    "supply_delta_pct",
    "property_price_delta_pct",
)


def run_decision_agent(
    question: str,
    property_features: PropertyFeatures,
    market_context: MarketContext,
    *,
    shocks: dict[str, float],
    years: int = 5,
    use_genai: bool = False,
    generate: Callable[[list[dict]], tuple[dict, dict]] | None = None,
) -> dict[str, Any]:
    """Execute a fixed, inspectable tool graph using *caller-selected* shocks.

    All financial inputs and model parameters are bounded at the API boundary.
    The language model cannot invent tool names, call the internet, execute code,
    access files, change scenario inputs, or turn synthetic data into real data.
    """
    if not question.strip() or len(question) > 500:
        raise ValueError("question must be 1..500 characters")
    if not 1 <= years <= 30:
        raise ValueError("years must be between 1 and 30")
    if set(shocks) - set(SHOCK_FIELDS):
        raise ValueError("Unknown scenario shock")
    if any(not isinstance(v, (int, float)) or not -100 <= v <= 100 for v in shocks.values()):
        raise ValueError("Scenario shocks must be finite and bounded")
    if generate is not None and not use_genai:
        raise ValueError("Injected generation requires opt-in")

    # Tool 1: existing transparent property baseline. Never claim this is fitted.
    property_result = analyze_property(
        property_features, market_context,
        data_classification=DataClassification.SYNTHETIC,
    )
    # Tools 2 and 3: paired Monte Carlo runs, identical seed and sample count.
    scenario_common = {
        "current_value_mxn": property_result["fair_value_mxn"],
        "annual_rent_mxn": property_result["expected_monthly_rent_mxn"] * 12,
        "years": years,
        "base_inflation_rate": market_context.annual_inflation,
    }
    baseline = simulate_property_returns(ScenarioInputs(**scenario_common), seed=42)
    stress = simulate_property_returns(
        ScenarioInputs(**scenario_common, **{name: shocks.get(name, 0) for name in SHOCK_FIELDS}),
        seed=42,
    )
    diff_return = round(
        stress["expected_real_total_return_pct"] - baseline["expected_real_total_return_pct"], 2
    )
    diff_loss = round(
        stress["probability_of_real_loss_pct"] - baseline["probability_of_real_loss_pct"], 2
    )
    comparison = {
        "expected_real_return_change_pp": diff_return,
        "real_loss_probability_change_pp": diff_loss,
        "same_seed": 42,
        "same_simulations": baseline["simulations"],
    }
    # Stable evidence anchors. Numeric claims in the primary response are copied
    # from tool results, not inferred or rewritten by a model.
    sources = [
        {
            "id": "property-analysis",
            "text": (
                f"Property synthetic baseline fair_value_mxn: {property_result['fair_value_mxn']}. "
                f"Property decision: {property_result['decision']}. "
                f"Estimated monthly rent MXN: {property_result['expected_monthly_rent_mxn']}."
            ),
        },
        {
            "id": "baseline-simulation",
            "text": (
                f"Baseline conditional scenario expected real total return pct: "
                f"{baseline['expected_real_total_return_pct']}. "
                f"Baseline probability of real loss pct: {baseline['probability_of_real_loss_pct']}."
            ),
        },
        {
            "id": "stress-simulation",
            "text": (
                f"Stress conditional scenario expected real total return pct: "
                f"{stress['expected_real_total_return_pct']}. "
                f"Stress probability of real loss pct: {stress['probability_of_real_loss_pct']}."
            ),
        },
        {
            "id": "paired-comparison",
            "text": (
                f"Paired synthetic scenario change in expected real return: {diff_return} "
                f"percentage points. Change in real loss probability: {diff_loss} percentage "
                f"points. Same random seed: 42. Samples per scenario: {baseline['simulations']}."
            ),
        },
    ]
    answer = (
        f"Synthetic conditional simulation over {years} years: the baseline expected real "
        f"total return is {baseline['expected_real_total_return_pct']}%, versus "
        f"{stress['expected_real_total_return_pct']}% under the supplied shocks "
        f"({diff_return:+.2f} percentage points). Estimated real-loss probability changes "
        f"from {baseline['probability_of_real_loss_pct']}% to "
        f"{stress['probability_of_real_loss_pct']}% ({diff_loss:+.2f} percentage points). "
        "These are conditional calculations from heuristic inputs, not market observations "
        "or investment advice."
    )
    # An optional model can only interpret serialized outputs of the bounded tools.
    # Its output is kept separate from the canonical deterministic explanation.
    generated = None
    if use_genai:
        generated = answer_with_quotes(
            "property baseline conditional scenario real return probability " + question,
            sources,
            generate=generate,
            top_k=4,
        )

    return {
        "question": question,
        "answer": answer,
        "generation_mode": "bounded_tool_orchestration",
        "data_classification": "synthetic",
        "tool_trace": [
            {"tool": "analyze_property", "source_id": "property-analysis"},
            {"tool": "simulate_property_returns", "variant": "baseline", "source_id": "baseline-simulation"},
            {"tool": "simulate_property_returns", "variant": "stress", "source_id": "stress-simulation"},
            {"tool": "compare_paired_scenarios", "source_id": "paired-comparison"},
        ],
        "property": property_result,
        "baseline": baseline,
        "stress": stress,
        "comparison": comparison,
        "sources": sources,
        "generated_interpretation": generated,
        "limitations": [
            "Synthetic demo market assumptions; not a real-world observation.",
            "The property value and uncertainty band are heuristic, not fitted/calibrated.",
            "Same-seed comparison reduces simulation noise; it does not validate assumptions.",
            "Optional model quotes are structurally checked, not proof of semantic truth.",
            "No general-purpose LLM tool execution, database writes, or web access.",
        ],
    }
