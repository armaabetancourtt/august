# Contributing to AUGUST

AUGUST welcomes contributions that improve the rigor, reproducibility or usefulness of the decision system.

## Before opening a model PR

Document:

- the business / decision question;
- dataset source and license/terms;
- whether data is real public, derived or synthetic;
- target population and time period;
- train / validation / test strategy;
- baseline;
- leakage checks;
- primary and secondary metrics;
- uncertainty / calibration where relevant;
- known limitations.

## Data rules

Never commit:

- credentials;
- private customer or transaction data;
- identity documents;
- proprietary datasets without redistribution rights.

Synthetic data must be clearly labeled.

## Code quality

Run:

```bash
ruff check src api pipelines tests
pytest
```

For the web app:

```bash
cd apps/web
npm install
npm run build
```

## Results

Do not add a performance number to the README unless the repository includes the reproducible command, dataset version, split strategy and evaluation code that generated it.

## Causal claims

A correlation or predictive association is not a causal result. Causal contributions must document the identification strategy and assumptions.
