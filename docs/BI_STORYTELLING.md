# BI + Data Storytelling in AUGUST

AUGUST includes a recruiter-visible analytics layer in addition to models, APIs and simulation.

> **Important:** the default dataset is deterministic synthetic demo data. The BI layer demonstrates the workflow, not real Mexican real-estate performance.

## What this demonstrates

The analytics surface is designed around the questions a business stakeholder asks:

1. **What changed?** — time-series and KPI movement.
2. **Where is it concentrated?** — neighborhood comparison.
3. **Why does it matter?** — inflation, financing and real-return context.
4. **What decision follows?** — a bounded next action, not an unsupported prediction.
5. **Can another analyst reproduce it?** — shared Python logic, API contract and flat BI exports.

This is the difference between charting data and doing data storytelling.

## Generate the BI datasets

Run:

~~~bash
python -m pipelines.bootstrap_demo
python -m pipelines.export_bi
~~~

The second command creates:

~~~text
data/processed/bi/
├── macro_monthly.csv
├── property_fact.csv
├── neighborhood_summary.csv
└── executive_kpis.csv
~~~

The files are generated artifacts and stay out of Git through .gitignore.

## Power BI build

Use **Get data → Text/CSV** and load the four generated files.

Recommended report pages:

### 1. Executive Overview

- KPI cards: 12-month housing-index change, inflation change, policy-rate change, median property price.
- Line chart: date vs housing_index.
- Line chart: date vs inflation_pct and policy_rate_pct.
- Bar chart: neighborhood vs median_price_m2.
- Narrative box: use the same Signal → Evidence → Implication → Next decision structure exposed by /v1/analytics/overview.

### 2. Property Explorer

- Slicer: neighborhood.
- Scatter: area_m2 vs price_mxn, legend by neighborhood.
- Distribution / histogram: price_m2.
- Detail table: property ID, area, beds, baths, price, price per m².

### 3. Market Context

- Macro trend charts.
- Latest value and 12-month delta cards.
- Explicit **SYNTHETIC DEMO** banner.

For a production model, introduce a Date dimension and stable neighborhood/location dimensions rather than relating aggregate files back to fact rows.

## Tableau build

Connect Tableau to the same CSV folder.

Recommended sheets:

- **Housing Momentum** — monthly housing index line.
- **Rates vs Inflation** — two-line monthly comparison.
- **Neighborhood Price / m²** — sorted horizontal bars.
- **Property Price Scatter** — area vs price until real geospatial data is introduced.
- **Executive Story** — dashboard text zones for signal, evidence, implication and next decision.

Combine the sheets into one dashboard and keep the synthetic-data warning visible.

## Reproducible report

Generate the Markdown executive report with:

~~~bash
python -m pipelines.generate_executive_report
~~~

The report is built from the same build_executive_overview() function used by the API. That keeps the dashboard, BI exports and written story aligned instead of letting three separate analyses drift apart.

## Portfolio talking point

A stronger interview explanation than “I made dashboards” is:

> I built one analytical contract that feeds an API, an interactive product dashboard, flat exports for Power BI/Tableau and a reproducible executive report. The same computed evidence drives every surface, and the narrative explicitly separates signal, evidence, implication and the next decision.

That demonstrates analytics engineering, visualization, stakeholder communication and product thinking in addition to machine learning.
