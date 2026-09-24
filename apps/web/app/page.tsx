"use client";

import { useEffect, useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_AUGUST_API_URL ?? "http://localhost:8000";

type MarketPulse = {
  market: string;
  data_classification: string;
  inflation_pct: number;
  policy_rate_pct: number;
  mxn_usd: number;
  housing_index: number;
  economic_momentum: string;
};

type ExecutiveOverview = {
  market: string;
  data_classification: string;
  as_of: string;
  kpis: {
    housing_change_12m_pct: number;
    inflation_change_12m_pp: number;
    policy_rate_change_12m_pp: number;
    fx_change_12m_pct: number;
    median_property_price_mxn: number;
    median_price_m2: number;
    property_count: number;
  };
  story: {
    headline: string;
    signal: string;
    evidence: string;
    implication: string;
    next_decision: string;
  };
  market_series: Array<{
    date: string;
    inflation_pct: number;
    policy_rate_pct: number;
    mxn_usd: number;
    economic_activity_index: number;
    housing_index: number;
  }>;
  neighborhoods: Array<{
    neighborhood: string;
    properties: number;
    median_price_mxn: number;
    median_price_m2: number;
    median_area_m2: number;
  }>;
  warning: string;
};

type Analysis = {
  decision: string;
  fair_value_mxn: number;
  fair_value_interval_95_like: [number, number];
  asking_price_mxn: number;
  asking_gap_pct: number;
  expected_monthly_rent_mxn: number;
  nominal_rental_yield_pct: number;
  real_rental_yield_pct: number;
  confidence: number;
  evidence: Array<{ label: string; value: number | string; method: string }>;
  assumptions: string[];
  limitations: string[];
};

type Scenario = {
  expected_total_return_pct: number;
  expected_real_total_return_pct: number;
  p10_total_return_pct: number;
  p50_total_return_pct: number;
  p50_real_return_pct: number;
  probability_of_nominal_loss_pct: number;
  probability_of_real_loss_pct: number;
  warning: string;
};

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "MXN",
  maximumFractionDigits: 0
});

export default function Home() {
  const [active, setActive] = useState("insights");
  const [market, setMarket] = useState<MarketPulse | null>(null);
  const [overview, setOverview] = useState<ExecutiveOverview | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [question, setQuestion] = useState("What is the main risk in this property?");
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);

  const [property, setProperty] = useState({
    city: "Synthetic Metro",
    neighborhood: "Central",
    asking_price_mxn: 6800000,
    area_m2: 148,
    bedrooms: 2,
    bathrooms: 2
  });

  const [shocks, setShocks] = useState({
    inflation_delta_pp: 0,
    mortgage_rate_delta_pp: 0,
    demand_delta_pct: 0,
    supply_delta_pct: 0,
    property_price_delta_pct: 0
  });

  useEffect(() => {
    fetch(`${API}/v1/market/pulse`)
      .then((r) => r.ok ? r.json() : Promise.reject(new Error("API unavailable")))
      .then(setMarket)
      .catch(() => setMarket(null));

    fetch(`${API}/v1/analytics/overview`)
      .then((r) => r.ok ? r.json() : Promise.reject(new Error("Analytics unavailable")))
      .then(setOverview)
      .catch(() => setOverview(null));
  }, []);

  const annualRent = useMemo(
    () => (analysis?.expected_monthly_rent_mxn ?? 0) * 12,
    [analysis]
  );

  async function analyze() {
    setBusy(true);
    setAnswer("");
    setScenario(null);
    try {
      const response = await fetch(`${API}/v1/properties/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(property)
      });
      if (!response.ok) throw new Error("Analysis failed");
      setAnalysis(await response.json());
      setActive("analyze");
    } finally {
      setBusy(false);
    }
  }

  async function runScenario() {
    if (!analysis) return;
    setBusy(true);
    try {
      const response = await fetch(`${API}/v1/scenarios/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_value_mxn: analysis.fair_value_mxn,
          annual_rent_mxn: annualRent,
          years: 5,
          base_inflation_rate: 0.045,
          ...shocks
        })
      });
      if (!response.ok) throw new Error("Scenario failed");
      setScenario(await response.json());
      setActive("scenario");
    } finally {
      setBusy(false);
    }
  }

  async function askAugust() {
    if (!analysis || !question.trim()) return;
    const response = await fetch(`${API}/v1/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, analysis })
    });
    if (!response.ok) return;
    const payload = await response.json();
    setAnswer(payload.answer);
    setActive("ask");
  }

  const nav = [
    ["insights", "01", "Insights"],
    ["market", "02", "Market"],
    ["analyze", "03", "Analyze"],
    ["scenario", "04", "Scenario Lab"],
    ["ask", "05", "Ask AUGUST"]
  ];

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <img src="/august-wordmark.svg" alt="AUGUST" className="brand-wordmark" width="188" height="67" />
        </div>
        <div className="brand-sub">DECISION INTELLIGENCE<br />& RISK ENGINE</div>

        <nav className="nav">
          {nav.map(([id, index, label]) => (
            <button
              key={id}
              className={active === id ? "active" : ""}
              onClick={() => {
                setActive(id);
                document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
              }}
            >
              <span className="nav-index">{index}</span>
              {label}
            </button>
          ))}
        </nav>

        <div className="demo-badge">
          SYNTHETIC DEMO<br />
          NO REAL MARKET CLAIMS
        </div>
      </aside>

      <main className="main">
        <div className="topline">
          <span><span className="live-dot" />ENGINE ONLINE</span>
          <span>FROM RAW SIGNALS TO DECISIONS.</span>
        </div>

        <header className="hero">
          <div className="hero-brand">
            <img src="/august-wordmark.svg" alt="AUGUST" width="1250" height="445" />
            <span className="hero-edition">INTELLIGENCE, BY DESIGN / 01</span>
          </div>
          <div className="kicker">DECISION INTELLIGENCE</div>
          <h1>Know what changes before the decision does.</h1>
          <p>
            AUGUST connects market context, property fundamentals, uncertainty
            and conditional scenarios. The product shows the decision first —
            then the evidence underneath it.
          </p>
          <div className="hero-rule" aria-hidden="true"><span>DECISIONS, BACKED BY EVIDENCE.</span><span>EST. 2026</span></div>
        </header>

        <section className="section executive-section" id="insights">
          <div className="section-head">
            <div>
              <h2 className="section-title">Executive insights</h2>
              <p className="section-copy">Charts are evidence. The story ends in a decision.</p>
            </div>
            <span className="decision-state">BI + STORYTELLING</span>
          </div>

          {overview ? (
            <>
              <div className="story-hero">
                <div>
                  <div className="story-eyebrow">THE STORY IN ONE SCREEN · {overview.as_of}</div>
                  <h3>{overview.story.headline}</h3>
                  <p>{overview.story.implication}</p>
                </div>
                <div className="story-next">
                  <span>NEXT DECISION</span>
                  <strong>{overview.story.next_decision}</strong>
                </div>
              </div>

              <div className="insight-kpis">
                <Metric
                  label="HOUSING · 12M"
                  value={`${overview.kpis.housing_change_12m_pct > 0 ? "+" : ""}${overview.kpis.housing_change_12m_pct}%`}
                  foot="synthetic index change"
                />
                <Metric
                  label="INFLATION · 12M"
                  value={`${overview.kpis.inflation_change_12m_pp > 0 ? "+" : ""}${overview.kpis.inflation_change_12m_pp} pp`}
                  foot="change in percentage points"
                />
                <Metric
                  label="MEDIAN PROPERTY"
                  value={money.format(overview.kpis.median_property_price_mxn)}
                  foot={`${overview.kpis.property_count} demo properties`}
                />
                <Metric
                  label="MEDIAN PRICE / M²"
                  value={money.format(overview.kpis.median_price_m2)}
                  foot="cross-market synthetic median"
                />
              </div>

              <div className="analytics-grid">
                <div className="panel chart-panel">
                  <div className="chart-head">
                    <div>
                      <span>MARKET TREND</span>
                      <strong>Housing index · last 24 months</strong>
                    </div>
                    <b>{overview.market_series.at(-1)?.housing_index.toFixed(1)}</b>
                  </div>
                  <HousingTrend data={overview.market_series} />
                </div>

                <div className="panel chart-panel">
                  <div className="chart-head">
                    <div>
                      <span>MACRO PRESSURE</span>
                      <strong>Inflation vs policy rate</strong>
                    </div>
                    <div className="chart-legend">
                      <i className="legend-dot accent-dot" />Inflation
                      <i className="legend-dot secondary-dot" />Policy rate
                    </div>
                  </div>
                  <RatesTrend data={overview.market_series} />
                </div>
              </div>

              <div className="analytics-grid lower-grid">
                <div className="panel">
                  <div className="chart-head">
                    <div>
                      <span>LOCAL PRICING</span>
                      <strong>Median price per m² by neighborhood</strong>
                    </div>
                  </div>
                  <NeighborhoodBars rows={overview.neighborhoods} />
                </div>

                <div className="panel story-panel">
                  <div className="story-step">
                    <span>01 · SIGNAL</span>
                    <p>{overview.story.signal}</p>
                  </div>
                  <div className="story-step">
                    <span>02 · EVIDENCE</span>
                    <p>{overview.story.evidence}</p>
                  </div>
                  <div className="story-step">
                    <span>03 · IMPLICATION</span>
                    <p>{overview.story.implication}</p>
                  </div>
                  <div className="story-step emphasis">
                    <span>04 · NEXT DECISION</span>
                    <p>{overview.story.next_decision}</p>
                  </div>
                </div>
              </div>

              <div className="bi-strip">
                <div>
                  <span>ANALYTICS DELIVERY</span>
                  <strong>One evidence layer → product dashboard → report → BI tools</strong>
                </div>
                <div className="bi-tags">
                  <b>POWER BI</b><b>TABLEAU</b><b>CSV</b><b>DUCKDB</b><b>FASTAPI</b>
                </div>
                <code>python -m pipelines.export_bi</code>
              </div>
            </>
          ) : (
            <div className="panel">
              <div className="decision-state">ANALYTICS API OFFLINE</div>
              <p className="section-copy">Start the FastAPI service to load the executive dashboard.</p>
            </div>
          )}
        </section>

        <section className="section" id="market">
          <div className="section-head">
            <div>
              <h2 className="section-title">Market pulse</h2>
              <p className="section-copy">Economic context before model output.</p>
            </div>
            <span className="decision-state">SYNTHETIC DATA</span>
          </div>

          <div className="metric-grid">
            <Metric label="INFLATION" value={market ? `${market.inflation_pct}%` : "—"} foot="annualized demo signal" />
            <Metric label="POLICY RATE" value={market ? `${market.policy_rate_pct}%` : "—"} foot="synthetic macro series" />
            <Metric label="MXN / USD" value={market ? market.mxn_usd.toFixed(2) : "—"} foot="synthetic FX series" />
            <Metric label="MOMENTUM" value={market?.economic_momentum ?? "—"} foot="latest period direction" />
          </div>
        </section>

        <section className="section" id="analyze">
          <div className="section-head">
            <div>
              <h2 className="section-title">Analyze a property</h2>
              <p className="section-copy">Transparent baseline before sophisticated models.</p>
            </div>
          </div>

          <div className="workspace">
            <div className="panel">
              <h3 className="panel-title">PROPERTY INPUT</h3>
              <div className="form-grid">
                <Field label="ASKING PRICE" value={property.asking_price_mxn} onChange={(v) => setProperty({ ...property, asking_price_mxn: v })} />
                <Field label="AREA · M²" value={property.area_m2} onChange={(v) => setProperty({ ...property, area_m2: v })} />
                <Field label="BEDROOMS" value={property.bedrooms} onChange={(v) => setProperty({ ...property, bedrooms: v })} />
                <Field label="BATHROOMS" value={property.bathrooms} onChange={(v) => setProperty({ ...property, bathrooms: v })} />
              </div>
              <button className="primary" onClick={analyze} disabled={busy}>
                {busy ? "ANALYZING…" : "ANALYZE PROPERTY"}
              </button>
              <p className="warning">Demo inputs are evaluated against synthetic market context. No investment claim is made.</p>
            </div>

            <div className="panel decision">
              {analysis ? (
                <>
                  <div className="decision-state">{analysis.decision}</div>
                  <div className="big-number">{money.format(analysis.fair_value_mxn)}</div>
                  <div className="big-caption">BASELINE FAIR VALUE · {Math.round(analysis.confidence * 100)}% heuristic confidence</div>
                  <div className="interval">
                    Uncertainty band {money.format(analysis.fair_value_interval_95_like[0])} → {money.format(analysis.fair_value_interval_95_like[1])}
                  </div>
                  <div className="scenario-result">
                    <ScenarioStat label="ASKING GAP" value={`${analysis.asking_gap_pct > 0 ? "+" : ""}${analysis.asking_gap_pct}%`} />
                    <ScenarioStat label="MONTHLY RENT" value={money.format(analysis.expected_monthly_rent_mxn)} />
                    <ScenarioStat label="NOMINAL YIELD" value={`${analysis.nominal_rental_yield_pct}%`} />
                    <ScenarioStat label="REAL YIELD" value={`${analysis.real_rental_yield_pct}%`} />
                  </div>
                  <div className="evidence">
                    {analysis.evidence.slice(0, 4).map((item) => (
                      <div className="evidence-row" key={item.label}>
                        <span>{item.label}</span>
                        <strong>{typeof item.value === "number" ? money.format(item.value) : item.value}</strong>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  <div className="decision-state">WAITING FOR PROPERTY</div>
                  <div className="big-number">—</div>
                  <div className="big-caption">AUGUST will show the decision before the evidence.</div>
                </>
              )}
            </div>
          </div>
        </section>

        <section className="section" id="scenario">
          <div className="section-head">
            <div>
              <h2 className="section-title">Scenario Lab</h2>
              <p className="section-copy">Change assumptions. Recompute the distribution.</p>
            </div>
          </div>

          <div className="panel">
            <div className="slider-stack">
              <Range label="INFLATION" value={shocks.inflation_delta_pp} min={-3} max={5} step={0.5} suffix=" pp" onChange={(v) => setShocks({ ...shocks, inflation_delta_pp: v })} />
              <Range label="MORTGAGE RATE" value={shocks.mortgage_rate_delta_pp} min={-4} max={5} step={0.5} suffix=" pp" onChange={(v) => setShocks({ ...shocks, mortgage_rate_delta_pp: v })} />
              <Range label="RENTAL DEMAND" value={shocks.demand_delta_pct} min={-30} max={30} step={5} suffix="%" onChange={(v) => setShocks({ ...shocks, demand_delta_pct: v })} />
              <Range label="LOCAL SUPPLY" value={shocks.supply_delta_pct} min={-30} max={40} step={5} suffix="%" onChange={(v) => setShocks({ ...shocks, supply_delta_pct: v })} />
            </div>

            <button className="primary" onClick={runScenario} disabled={!analysis || busy}>
              RUN 10,000 CONDITIONAL SCENARIOS
            </button>

            {scenario ? (
              <>
                <div className="scenario-result">
                  <ScenarioStat label="EXPECTED REAL 5Y RETURN" value={`${scenario.expected_real_total_return_pct}%`} />
                  <ScenarioStat label="REAL P50" value={`${scenario.p50_real_return_pct}%`} />
                  <ScenarioStat label="NOMINAL P10" value={`${scenario.p10_total_return_pct}%`} />
                  <ScenarioStat label="REAL LOSS PROBABILITY" value={`${scenario.probability_of_real_loss_pct}%`} />
                </div>
                <p className="warning">{scenario.warning}</p>
              </>
            ) : null}
          </div>
        </section>

        <section className="section" id="ask">
          <div className="section-head">
            <div>
              <h2 className="section-title">Ask AUGUST</h2>
              <p className="section-copy">Language after analytics — never instead of analytics.</p>
            </div>
          </div>

          <div className="panel">
            <div className="ask-box">
              <input value={question} onChange={(e) => setQuestion(e.target.value)} />
              <button onClick={askAugust} disabled={!analysis}>ASK</button>
            </div>
            {answer ? <div className="answer">{answer}</div> : null}
            <p className="warning">Current mode is deterministic structured explanation. A local LLM is a later, evaluated layer.</p>
          </div>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value, foot }: { label: string; value: string; foot: string }) {
  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-foot">{foot}</div>
    </div>
  );
}

function chartPoints(values: number[], width = 640, height = 190, pad = 16) {
  if (!values.length) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, 0.0001);
  return values.map((value, index) => {
    const x = pad + (index / Math.max(values.length - 1, 1)) * (width - pad * 2);
    const y = height - pad - ((value - min) / span) * (height - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

function HousingTrend({ data }: { data: ExecutiveOverview["market_series"] }) {
  const values = data.map((row) => row.housing_index);
  const min = Math.min(...values);
  const max = Math.max(...values);
  return (
    <div className="chart-wrap">
      <div className="chart-scale"><span>{max.toFixed(0)}</span><span>{min.toFixed(0)}</span></div>
      <svg className="chart-svg" viewBox="0 0 640 190" role="img" aria-label="Housing index trend">
        {[0, 1, 2, 3, 4].map((line) => (
          <line key={line} x1="16" x2="624" y1={16 + line * 39.5} y2={16 + line * 39.5} className="chart-gridline" />
        ))}
        <polyline points={chartPoints(values)} className="chart-line chart-line-accent" />
      </svg>
      <div className="chart-axis"><span>{data[0]?.date}</span><span>{data.at(-1)?.date}</span></div>
    </div>
  );
}

function RatesTrend({ data }: { data: ExecutiveOverview["market_series"] }) {
  const inflation = data.map((row) => row.inflation_pct);
  const policy = data.map((row) => row.policy_rate_pct);
  const all = [...inflation, ...policy];
  const min = Math.min(...all);
  const max = Math.max(...all);
  const width = 640;
  const height = 190;
  const pad = 16;
  const span = Math.max(max - min, 0.0001);
  const points = (values: number[]) => values.map((value, index) => {
    const x = pad + (index / Math.max(values.length - 1, 1)) * (width - pad * 2);
    const y = height - pad - ((value - min) / span) * (height - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");

  return (
    <div className="chart-wrap">
      <div className="chart-scale"><span>{max.toFixed(1)}%</span><span>{min.toFixed(1)}%</span></div>
      <svg className="chart-svg" viewBox="0 0 640 190" role="img" aria-label="Inflation and policy rate trend">
        {[0, 1, 2, 3, 4].map((line) => (
          <line key={line} x1="16" x2="624" y1={16 + line * 39.5} y2={16 + line * 39.5} className="chart-gridline" />
        ))}
        <polyline points={points(inflation)} className="chart-line chart-line-accent" />
        <polyline points={points(policy)} className="chart-line chart-line-secondary" />
      </svg>
      <div className="chart-axis"><span>{data[0]?.date}</span><span>{data.at(-1)?.date}</span></div>
    </div>
  );
}

function NeighborhoodBars({ rows }: { rows: ExecutiveOverview["neighborhoods"] }) {
  const max = Math.max(...rows.map((row) => row.median_price_m2), 1);
  return (
    <div className="bar-list">
      {rows.map((row) => (
        <div className="bar-row" key={row.neighborhood}>
          <div className="bar-label">
            <strong>{row.neighborhood}</strong>
            <span>{row.properties} properties</span>
          </div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${(row.median_price_m2 / max) * 100}%` }} />
          </div>
          <div className="bar-value">{money.format(row.median_price_m2)}</div>
        </div>
      ))}
    </div>
  );
}

function Field({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input type="number" value={value} onChange={(e) => onChange(Number(e.target.value))} />
    </div>
  );
}

function Range({
  label, value, min, max, step, suffix, onChange
}: {
  label: string; value: number; min: number; max: number; step: number; suffix: string;
  onChange: (value: number) => void;
}) {
  return (
    <div className="range-row">
      <label>{label}</label>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} />
      <div className="range-value">{value > 0 ? "+" : ""}{value}{suffix}</div>
    </div>
  );
}

function ScenarioStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="scenario-stat">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
