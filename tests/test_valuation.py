from august.real_estate.valuation import MarketContext, PropertyFeatures, analyze_property


def test_property_analysis_exposes_assumptions_and_provenance():
    result = analyze_property(
        PropertyFeatures(
            city="Synthetic Metro",
            neighborhood="Central",
            asking_price_mxn=6_800_000,
            area_m2=148,
            bedrooms=2,
            bathrooms=2,
        ),
        MarketContext(
            neighborhood_price_m2=49_500,
            annual_inflation=0.045,
            mortgage_rate=0.103,
            rental_yield=0.052,
            demand_index=1.04,
            supply_index=0.98,
        ),
    )
    assert result["assumptions"]
    assert result["limitations"]
    assert result["provenance"][0]["classification"] == "synthetic"
