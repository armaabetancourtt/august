# AUGUST Intelligence — bounded analytical agent

The **POST /v1/agent/analyze** endpoint executes an inspectable, allowlisted
workflow rather than delegating arbitrary tool calls to the LLM:

1. Validate caller-provided property and bounded numeric shocks.
2. Execute the existing heuristic synthetic property baseline.
3. Derive annual rent from that result and run 10,000 baseline Monte Carlo draws.
4. Re-run with the caller's shocks under the **same seed (42)**.
5. Compute differences in percentage points from the returned tool values.
6. Return canonical numeric answers, original tool outputs and four source anchors.
7. Optionally, with explicit opt-in and configured provider, generate independent
   commentary using only those four source excerpts and exact-quote validation.

A generated claim is NOT proof of semantic truth; the deterministic answer is
canonical. The model does not choose arbitrary tools, execute SQL/Python, search
the internet, write databases, or adjust numerical inputs. The original
POST /v1/ask and POST /v1/ask/grounded endpoints remain unchanged.

## Run

    python -m pip install -e '.[dev]'
    pytest tests/test_tool_agent.py
    uvicorn api.main:app --reload

    curl -X POST http://localhost:8000/v1/agent/analyze \
      -H 'Content-Type: application/json' \
      -d '{"question":"How would higher rates change expected real returns?","property":{"asking_price_mxn":6800000,"area_m2":148,"bedrooms":2,"bathrooms":2},"shocks":{"mortgage_rate_delta_pp":2}}'

The Next.js **AUGUST Intelligence** panel calls this endpoint after the property
analysis. Turn on the optional checkbox to send only four synthetic source
snippets to the external provider. Configure OPENAI_API_KEY and AUGUST_LLM_MODEL
server-side to enable that mode; do not put keys in NEXT_PUBLIC variables.

## Evidence and limitations

- All data are SYNTHETIC; no market observation, fitted property valuation, or
  calibrated probability is claimed.
- The same random seed reduces noise between scenarios, but does not establish
  causal effects or validate the assumed coefficients.
- Quotes are checked as exact substrings of returned synthetic tool snippets;
  the model's interpretation still requires human review.
- Scenario inputs are bounded at the FastAPI boundary; the tool names and
  execution order are fixed. No arbitrary URLs, file contents, database
  queries, or free-form code from users or models are executed.
- Local tests use synthetic fixtures and injected fake model responses;
  no claim of verified live-provider quality or production readiness.
