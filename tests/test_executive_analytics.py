from august.analytics.executive import build_executive_overview


def test_executive_overview_is_deterministic_and_bi_ready():
    result = build_executive_overview()

    assert result["data_classification"] == "synthetic"
    assert result["market"] == "SYNTHETIC METRO"
    assert result["kpis"]["property_count"] == 400
    assert len(result["market_series"]) == 24
    assert len(result["neighborhoods"]) == 4
    assert (
        result["neighborhoods"][0]["median_price_m2"]
        >= result["neighborhoods"][-1]["median_price_m2"]
    )
    assert "headline" in result["story"]
    assert "next_decision" in result["story"]
    assert result["bi_contract"]["grain_properties"] == "one row per property"


def test_executive_overview_expected_demo_snapshot():
    result = build_executive_overview()

    assert result["as_of"] == "2026-08-01"
    assert result["kpis"]["housing_change_12m_pct"] == 7.97
    assert result["kpis"]["inflation_change_12m_pp"] == -0.35
    assert result["neighborhoods"][0]["neighborhood"] == "West"
