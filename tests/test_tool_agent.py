from fastapi.testclient import TestClient
import pytest

from api.main import app, demo_market_context
from august.llm.grounded import GroundingError
from august.llm.tool_agent import run_decision_agent
from august.real_estate.valuation import PropertyFeatures

PROPERTY = {
    "city": "Synthetic Metro", "neighborhood": "Central",
    "asking_price_mxn": 6_800_000, "area_m2": 148,
    "bedrooms": 2, "bathrooms": 2,
}


def run(**overrides):
    return run_decision_agent(
        "Compare baseline and stress real return",
        PropertyFeatures(**PROPERTY),
        demo_market_context(),
        shocks={"mortgage_rate_delta_pp": 2.0},
        **overrides,
    )


def test_paired_runs_are_reproducible_and_cite_computed_values():
    first, second = run(), run()
    assert first == second
    assert first["data_classification"] == "synthetic"
    assert len(first["tool_trace"]) == 4
    assert first["comparison"]["expected_real_return_change_pp"] < 0
    assert str(first["stress"]["expected_real_total_return_pct"]) in first["answer"]
    assert first["generated_interpretation"] is None


def test_zero_shocks_produce_zero_delta():
    result = run_decision_agent(
        "Compare synthetic scenarios",
        PropertyFeatures(**PROPERTY),
        demo_market_context(),
        shocks={},
    )
    assert result["baseline"] == result["stress"]
    assert result["comparison"]["expected_real_return_change_pp"] == 0
    assert result["comparison"]["real_loss_probability_change_pp"] == 0


def test_model_cannot_fabricate_source_or_modify_canonical_calculations():
    with pytest.raises(GroundingError):
        run(
            use_genai=True,
            generate=lambda _: ({
                "claims": [{
                    "text": "Made up", "source_id": "unauthorized-source",
                    "quote": "a quote that never existed",
                }]
            }, {}),
        )


def test_optional_model_keeps_claims_separate_from_actual_tool_outputs():
    baseline = run()
    result = run(
        use_genai=True,
        generate=lambda _: ({
            "claims": [{
                "text": "The source lists a synthetic baseline.",
                "source_id": "property-analysis",
                "quote": "Property synthetic baseline",
            }]
        }, {"prompt_tokens": 10}),
    )
    assert result["answer"] == baseline["answer"]
    assert result["property"] == baseline["property"]
    assert result["generated_interpretation"]["claims"][0]["source_id"] == "property-analysis"


def test_api_runs_without_llm_keys_and_validates_shock_ranges(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AUGUST_LLM_MODEL", raising=False)
    client = TestClient(app)
    payload = {
        "question": "What changes in real return?",
        "property": PROPERTY, "shocks": {"mortgage_rate_delta_pp": 2},
    }
    response = client.post("/v1/agent/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["generation_mode"] == "bounded_tool_orchestration"
    assert client.post(
        "/v1/agent/analyze",
        json={**payload, "shocks": {"mortgage_rate_delta_pp": 1000}},
    ).status_code == 422
    assert client.post(
        "/v1/agent/analyze",
        json={**payload, "use_genai": True},
    ).status_code == 503
