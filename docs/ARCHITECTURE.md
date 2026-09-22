# Architecture

AUGUST separates **data**, **models**, **decisions** and **language**.

## Data plane

Public data adapters ingest versioned source observations. Validation occurs before data enters DuckDB.

SQL is a first-class analytics layer rather than hiding every transformation inside pandas.

## Intelligence plane

Reusable Python modules implement forecasting, econometrics, valuation, scenario simulation, fraud decisions, anomaly detection, experimentation and causal analysis.

Exploration may happen in notebooks, but production logic moves into `src/august`.

## Decision plane

Models do not directly write product prose.

They emit structured results containing evidence, uncertainty, assumptions, limitations and provenance.

## Language plane

Ask AUGUST consumes those structured outputs. A local/open-weight LLM may rewrite them, but it cannot invent missing metrics or causal explanations.

## Product plane

FastAPI provides a stable contract to the Next.js interface.

The product is decision-first: show the consequence, then let the analyst inspect evidence.
