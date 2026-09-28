# Grounded generative analyst (experimental)

**Implemented in this branch:** optional OpenAI chat-completions integration, lexical TF-IDF retrieval on explicitly provided text sources, structured claim output, exact substring checks for every source quote, unique source IDs and bounded inputs. Model output referring to an unretrieved source or a fabricated quote is rejected. The legacy `/v1/ask` deterministic endpoint remains unchanged; the opt-in generative endpoint is `POST /v1/ask/grounded`.

## Run locally

```bash
python -m pip install -e '.[dev]'
pytest tests/test_llm_grounded.py
export OPENAI_API_KEY='your-private-key'
export AUGUST_LLM_MODEL='explicit-json-capable-model-id'
uvicorn api.main:app
```

Example payload (the operator provides the actual documents, not a live search):

```json
{"question":"What is documented?","documents":[{"id":"note-01","text":"The official note documents an observation."}]}
```

The response supplies claim text, source ID and exact quote anchor. If lexical retrieval finds nothing relevant, it returns `insufficient_evidence` without calling the model. Requests fail closed without configuration. This service does not autonomously browse the web, execute tools or retrieve private documents.

## Evaluation evidence

The `evaluate_retrieval_cases` function calculates hit@k and recall@k against caller-provided relevance labels. Tests cover known fixtures, fabricated quotes, fabricated IDs, an adversarial source attempting to supply instructions, no-overlap retrieval and missing credentials. The fixtures establish harness behavior **only**, not real-world retrieval, factuality or safety performance. Store independently curated cases, failures, usage, p95 latency, current pricing and documented model versions before publishing empirical benchmark scores.

The validator checks that the exact quote appears in its selected source and that the source was retrieved. It **does not prove** that a model-generated interpretation follows logically from that quote; human review and independent judgment are still needed. Tool isolation (there are no tools in this endpoint) narrows the prompt-injection impact but is not a comprehensive defense. Never send sensitive material or real account data to a third-party provider without permission.
