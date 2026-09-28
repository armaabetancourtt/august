from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from august.analytics.executive import build_executive_overview
from august.core.contracts import DataClassification
from august.fraud.decision import decide_transaction
from august.llm.analyst import explain_structured_analysis
from august.llm.grounded import GroundingError, answer_with_quotes
from august.llm.tool_agent import run_decision_agent
from august.real_estate.valuation import MarketContext, PropertyFeatures, analyze_property
from august.scenario.monte_carlo import ScenarioInputs, simulate_property_returns
from august.synthetic.demo import generate_macro_history

app = FastAPI(
    title="AUGUST API",
    version="0.1.0",
    description="Decision Intelligence & Risk Engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class PropertyRequest(BaseModel):
    city: str = "Synthetic Metro"
    neighborhood: str = "Central"
    asking_price_mxn: float = Field(gt=0)
    area_m2: float = Field(gt=0)
    bedrooms: int = Field(ge=0, le=10)
    bathrooms: float = Field(ge=0, le=10)


class ScenarioRequest(BaseModel):
    current_value_mxn: float = Field(gt=0)
    annual_rent_mxn: float = Field(ge=0)
    years: int = Field(default=5, ge=1, le=30)
    base_inflation_rate: float = Field(default=0.045, gt=-1, lt=1)
    inflation_delta_pp: float = 0.0
    mortgage_rate_delta_pp: float = 0.0
    demand_delta_pct: float = 0.0
    supply_delta_pct: float = 0.0
    property_price_delta_pct: float = 0.0


class RiskDecisionRequest(BaseModel):
    fraud_probability: float = Field(ge=0, le=1)
    transaction_amount: float = Field(ge=0)
    review_threshold: float = Field(default=0.25, ge=0, le=1)
    block_threshold: float = Field(default=0.80, ge=0, le=1)
    review_cost: float = Field(default=40.0, ge=0)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    analysis: dict


class SourceDocument(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    text: str = Field(min_length=1, max_length=5000)


class GroundedAskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    documents: list[SourceDocument] = Field(min_length=1, max_length=12)


class AgentShocks(BaseModel):
    inflation_delta_pp: float = Field(default=0, ge=-3, le=5, allow_inf_nan=False)
    mortgage_rate_delta_pp: float = Field(default=0, ge=-4, le=5, allow_inf_nan=False)
    demand_delta_pct: float = Field(default=0, ge=-30, le=30, allow_inf_nan=False)
    supply_delta_pct: float = Field(default=0, ge=-30, le=40, allow_inf_nan=False)
    property_price_delta_pct: float = Field(default=0, ge=-30, le=30, allow_inf_nan=False)


class AgentRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    property: PropertyRequest
    shocks: AgentShocks = Field(default_factory=AgentShocks)
    years: int = Field(default=5, ge=1, le=30)
    use_genai: bool = False


def demo_market_context() -> MarketContext:
    return MarketContext(
        neighborhood_price_m2=49_500,
        annual_inflation=0.045,
        mortgage_rate=0.103,
        rental_yield=0.052,
        demand_index=1.04,
        supply_index=0.98,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "august-api", "version": "0.1.0"}


@app.get("/v1/analytics/overview")
def analytics_overview() -> dict:
    return build_executive_overview()


@app.get("/v1/market/pulse")
def market_pulse() -> dict:
    frame = generate_macro_history()
    latest = frame.iloc[-1]
    previous = frame.iloc[-2]

    return {
        "market": "SYNTHETIC METRO",
        "data_classification": "synthetic",
        "as_of": str(latest["date"].date()),
        "inflation_pct": round(float(latest["inflation"]) * 100, 2),
        "policy_rate_pct": round(float(latest["policy_rate"]) * 100, 2),
        "mxn_usd": round(float(latest["mxn_usd"]), 2),
        "housing_index": round(float(latest["housing_index"]), 2),
        "economic_momentum": (
            "IMPROVING"
            if latest["economic_activity_index"] > previous["economic_activity_index"]
            else "SLOWING"
        ),
        "warning": "Synthetic demo data. Not an observation about Mexico or any real market.",
    }


@app.post("/v1/properties/analyze")
def property_analysis(request: PropertyRequest) -> dict:
    result = analyze_property(
        PropertyFeatures(**request.model_dump()),
        demo_market_context(),
        data_classification=DataClassification.SYNTHETIC,
    )
    result["data_classification"] = "synthetic"
    result["product_mode"] = "baseline_demo"
    return result


@app.post("/v1/scenarios/simulate")
def scenario(request: ScenarioRequest) -> dict:
    result = simulate_property_returns(ScenarioInputs(**request.model_dump()))
    result["data_classification"] = "synthetic"
    return result


@app.post("/v1/risk/decision")
def risk_decision(request: RiskDecisionRequest) -> dict:
    result = decide_transaction(
        request.fraud_probability,
        request.transaction_amount,
        review_threshold=request.review_threshold,
        block_threshold=request.block_threshold,
        review_cost=request.review_cost,
    )
    result["decision_basis"] = "expected_loss_thresholding"
    result["warning"] = (
        "Decision layer only. fraud_probability must come from a separately validated model."
    )
    return result


@app.post("/v1/ask")
def ask(request: AskRequest) -> dict:
    return explain_structured_analysis(request.question, request.analysis)


@app.post("/v1/ask/grounded")
def ask_grounded(request: GroundedAskRequest) -> dict:
    """Opt-in external provider. Caller explicitly supplies source documents."""
    try:
        return answer_with_quotes(
            request.question, [item.model_dump() for item in request.documents]
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GroundingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/agent/analyze")
def agent_analysis(request: AgentRequest) -> dict:
    """Fixed analytic tool graph with optional, explicitly enabled LLM commentary."""
    try:
        return run_decision_agent(
            request.question,
            PropertyFeatures(**request.property.model_dump()),
            demo_market_context(),
            shocks=request.shocks.model_dump(),
            years=request.years,
            use_genai=request.use_genai,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (GroundingError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
