# Power BI — Semantic Layer

Default source: generated CSV files from python -m pipelines.export_bi.

> All default values are synthetic demo data.

## Core measures

### Property Count

    Property Count =
    COUNTROWS(property_fact)

### Median Property Price

    Median Property Price =
    MEDIAN(property_fact[price_mxn])

### Median Price per m²

    Median Price per m² =
    MEDIAN(property_fact[price_m2])

### Latest Housing Index

    Latest Housing Index =
    VAR LatestDate = MAX(macro_monthly[date])
    RETURN
        CALCULATE(
            MAX(macro_monthly[housing_index]),
            macro_monthly[date] = LatestDate
        )

### Housing Index 12M Change %

    Housing Index 12M Change % =
    VAR LatestDate = MAX(macro_monthly[date])
    VAR LatestValue =
        CALCULATE(
            MAX(macro_monthly[housing_index]),
            macro_monthly[date] = LatestDate
        )
    VAR PriorValue =
        CALCULATE(
            MAX(macro_monthly[housing_index]),
            DATEADD(macro_monthly[date], -12, MONTH)
        )
    RETURN
        DIVIDE(LatestValue - PriorValue, PriorValue)

Format this measure as Percentage.

### Latest Inflation %

    Latest Inflation % =
    VAR LatestDate = MAX(macro_monthly[date])
    RETURN
        CALCULATE(
            MAX(macro_monthly[inflation_pct]),
            macro_monthly[date] = LatestDate
        )

### Latest Policy Rate %

    Latest Policy Rate % =
    VAR LatestDate = MAX(macro_monthly[date])
    RETURN
        CALCULATE(
            MAX(macro_monthly[policy_rate_pct]),
            macro_monthly[date] = LatestDate
        )

## Executive Overview page

Use:

- four KPI cards;
- housing-index line chart;
- inflation and policy-rate line chart;
- horizontal neighborhood price/m² ranking;
- a text panel with Signal → Evidence → Implication → Next decision;
- a persistent SYNTHETIC DEMO warning.

For production, create a proper Date table and mark it as the model's date table before relying on time-intelligence measures.
