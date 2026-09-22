from august.scenario.monte_carlo import ScenarioInputs, simulate_property_returns


def test_scenario_is_reproducible():
    inputs = ScenarioInputs(current_value_mxn=5_000_000, annual_rent_mxn=300_000)
    first = simulate_property_returns(inputs, simulations=2_000, seed=7)
    second = simulate_property_returns(inputs, simulations=2_000, seed=7)
    assert first == second


def test_higher_rate_shock_reduces_expected_return():
    base = ScenarioInputs(current_value_mxn=5_000_000, annual_rent_mxn=300_000)
    stress = ScenarioInputs(
        current_value_mxn=5_000_000,
        annual_rent_mxn=300_000,
        mortgage_rate_delta_pp=2.0,
    )
    base_result = simulate_property_returns(base, simulations=3_000, seed=9)
    stress_result = simulate_property_returns(stress, simulations=3_000, seed=9)
    assert stress_result["expected_total_return_pct"] < base_result["expected_total_return_pct"]
