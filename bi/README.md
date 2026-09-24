<p align="center">
  <a href="../README.md"><img src="../docs/assets/august-brand-banner.svg" alt="AUGUST brand banner" width="560" /></a>
</p>

# AUGUST BI Workspace

This folder makes the BI layer visible in the repository instead of leaving Power BI and Tableau as résumé keywords.

The data is generated with:

    python -m pipelines.export_bi

Generated CSVs land in data/processed/bi/ and remain untracked because they are reproducible artifacts.

## Power BI

See powerbi/MEASURES.md for a small semantic-model and DAX layer. Build the report from:

- macro_monthly.csv
- property_fact.csv
- neighborhood_summary.csv
- executive_kpis.csv

Recommended pages: Executive Overview, Property Explorer, Market Context.

## Tableau

See tableau/CALCULATED_FIELDS.md for calculated fields and dashboard structure.

## Shared storytelling contract

Both tools should tell the same story as AUGUST Web:

**Signal → Evidence → Implication → Next decision**

A BI dashboard is not treated as the source of truth. Python computes the metrics first; BI tools consume clean, reproducible outputs.
