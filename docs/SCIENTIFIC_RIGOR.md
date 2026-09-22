# Scientific Rigor

AUGUST is designed as if its outputs could influence a real financial decision.

## Analysis contract

Every analysis must state:

1. decision question / hypothesis;
2. population and time period;
3. dataset and provenance;
4. target / treatment / outcome where applicable;
5. assumptions;
6. baseline;
7. validation strategy;
8. uncertainty;
9. limitations;
10. decision consequence.

## Forecasting

Forecast selection cannot be based on one convenient holdout.

Use rolling-origin or time-series cross-validation and report error by horizon. Include naive baselines. Inspect residuals, bias and interval coverage.

## Classification / fraud

Accuracy is not a primary metric for imbalanced fraud.

Prioritize PR-AUC, precision/recall at operational review capacity, calibration and expected business cost.

A threshold is a decision parameter, not a universal property of the classifier.

## Causal inference

Correlation is not causal evidence.

Every causal analysis must identify treatment, outcome, confounders, identification strategy, assumptions and threats to validity.

Difference-in-Differences requires a defensible parallel-trends argument. Propensity methods require overlap and measured-confounder assumptions.

## Synthetic data

Synthetic data is useful for engineering and testing, not for making empirical claims.

All synthetic output must remain visibly labeled.
