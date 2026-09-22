# Tableau — Calculated Fields + Dashboard Story

Default source: generated CSV files from python -m pipelines.export_bi.

> All default values are synthetic demo data.

## Property calculated fields

### Price per m²

    [price_mxn] / [area_m2]

### Price band

    IF [price_m2] >= 60000 THEN "Premium"
    ELSEIF [price_m2] >= 50000 THEN "Upper"
    ELSEIF [price_m2] >= 42000 THEN "Core"
    ELSE "Value"
    END

## Market calculated fields

### Latest month flag

    [date] = { FIXED : MAX([date]) }

### Latest housing index

    IF [Latest month flag] THEN [housing_index] END

### Latest inflation

    IF [Latest month flag] THEN [inflation_pct] END

### Latest policy rate

    IF [Latest month flag] THEN [policy_rate_pct] END

## Recommended sheets

1. Housing Momentum — date vs housing_index.
2. Rates vs Inflation — date vs inflation_pct and policy_rate_pct.
3. Neighborhood Price / m² — sorted median bars.
4. Property Explorer — area_m2 vs price_mxn, color by neighborhood.
5. Price Distribution — histogram of price_m2.

## Dashboard layout

Top row: KPI cards.

Middle row: Housing Momentum + Rates vs Inflation.

Bottom row: Neighborhood ranking + a text story.

The text story should follow:

**Signal → Evidence → Implication → Next decision**

Do not infer causal impact from the synthetic trend charts. The dashboard is an analytics communication demo, not a claim about a real market.
