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

type Analysis = {
  decision: string;
  fair_value_mxn: number;
  fair_value_interval_95_like: [number, number];
  asking_price_mxn: number;
  asking_gap_pct: number;
  expected_monthly_rent_mxn: number;
  confidence: number;
  evidence: Array<{ label: string; value: number | string; method: string }>;
  assumptions: string[];
  limitations: string[];
};

type Scenario = {
  expected_total_return_pct: number;
  p10_total_return_pct: number;
  p50_total_return_pct: number;
  p90_total_return_pct: number;
  probability_of_nominal_loss_pct: number;
  expected_downside_mxn: number;
  warning: string;
};

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "MXN",
  maximumFractionDigits: 0
});

export default function Home() {
  const [active, setActive] = useState("market");
  const [market, setMarket] = useState<MarketPulse | null>(null);
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
    ["market", "01", "Market"],
    ["analyze", "02", "Analyze"],
    ["scenario", "03", "Scenario Lab"],
    ["ask", "04", "Ask AUGUST"]
  ];

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">AUGUST</div>
        <div className="brand-sub">DECISION INTELLIGENCE<br />& RISK ENGINE</div>

        <nav className="nav">
          {nav.map(([id, index, label]) => (
            <button
              key={id}
              className={active === id ? "active" : ""}
              onClick={() => setActive(id)}
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
          <div className="kicker">DECISION INTELLIGENCE</div>
          <h1>Know what changes before the decision does.</h1>
          <p>
            AUGUST connects market context, property fundamentals, uncertainty
            and conditional scenarios. The product shows the decision first —
            then the evidence underneath it.
          </p>
        </header>

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
                  <ScenarioStat label="EXPECTED 5Y RETURN" value={`${scenario.expected_total_return_pct}%`} />
                  <ScenarioStat label="P10" value={`${scenario.p10_total_return_pct}%`} />
                  <ScenarioStat label="P50" value={`${scenario.p50_total_return_pct}%`} />
                  <ScenarioStat label="LOSS PROBABILITY" value={`${scenario.probability_of_nominal_loss_pct}%`} />
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
