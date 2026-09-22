# Data Sources

AUGUST prioritizes sources that another engineer can reproduce.

## Real public sources

### INEGI
Use for Mexican economic, labor, price and activity indicators when a stable public series/API is available.

### Banco de México / SIE
Use for policy rates, exchange-rate and financial series. Tokens belong in environment variables.

### FRED
The repository includes a generic CSV-series adapter. Series IDs must be documented alongside the analysis that uses them.

### Inside Airbnb
Useful for public short-term rental listing snapshots where the dataset and its terms permit the intended analysis.

## Provenance requirements

Every ingested table should retain:

- source;
- series/dataset identifier;
- observation date;
- retrieval date;
- data classification;
- transformation version.

No pipeline may silently replace failed public ingestion with synthetic data.
