# AUGUST — Executive Analytics Snapshot

> **SYNTHETIC DEMO DATA — NOT A REAL MARKET CLAIM**

**Snapshot:** seed 42 · **As of:** 2026-08-01

## Executive readout

### Synthetic housing index rose 8.0% YoY while inflation eased 0.35 pp.

**Signal.** Pricing momentum is up, inflation is down, and the policy-rate signal is broadly flat.

**Evidence.** The synthetic housing index changed **+7.97%** over 12 months, inflation moved **-0.35 pp**, and the policy rate moved **+0.10 pp**. Among the four demo neighborhoods, **West** has the highest median price per m² at approximately **MXN 60,605**.

**Why it matters.** Nominal appreciation by itself does not establish attractive real returns. Financing conditions, inflation and local pricing dispersion can materially change the decision.

**Next decision.** Underwrite at the neighborhood level, then stress-test financing and real-return downside before treating appreciation as durable value creation.

## KPI snapshot

| KPI | Synthetic value |
|---|---:|
| Housing index, 12m change | +7.97% |
| Inflation, 12m change | -0.35 pp |
| Policy rate, 12m change | +0.10 pp |
| MXN/USD series, 12m change | -3.59% |
| Median property price | MXN 6,219,296 |
| Median price / m² | MXN 50,096 |
| Properties in demo | 400 |

## Neighborhood comparison

| Neighborhood | Properties | Median MXN/m² | Median price | Median area |
|---|---:|---:|---:|---:|
| West | 118 | 60,605 | MXN 7,184,490 | 118.2 m² |
| Central | 116 | 50,214 | MXN 6,403,856 | 129.3 m² |
| South | 66 | 46,887 | MXN 6,436,693 | 136.1 m² |
| North | 100 | 41,481 | MXN 4,839,447 | 120.9 m² |

## Storytelling structure

AUGUST uses a repeatable four-part pattern instead of dumping charts on the reader:

**Signal → Evidence → Implication → Next decision**

The interactive web dashboard and the generated report use the same analytical contract, so the numbers and narrative stay synchronized.

## Reproduce

~~~bash
python -m pipelines.generate_executive_report
python -m pipelines.export_bi
~~~

The first command regenerates the written report. The second produces Power BI / Tableau-ready CSV datasets under data/processed/bi/.
