# Local and managed integrations

**Ready to configure, not deployed**: Airflow DAG in `airflow_dbt.py` executes `dbt parse` then `dbt build` on an existing warehouse. Configure `AUGUST_REPO_ROOT`, dbt adapter and credentials in the worker runtime. dbt models require an existing `raw.property_events` table with explicit consent and retention policy.

**Kafka**: `pip install -r pipelines/requirements-streaming.txt`; then run `python -m pipelines.kafka_property_consumer --output /secured/landing.jsonl`. It commits offsets after flushing valid events, but lacks durable transactional coordination and a dead-letter queue; add production-grade recovery before operational use.

**ML**: `python -m ml.pytorch_regression` or `python -m ml.tensorflow_forecast` after installing separate optional ML requirements. Both intentionally learn from **synthetic** numbers; neither is evidence of a deployed valuation or fraud model.

**Math**: gradient descent and automatic differentiation optimize squared error; evaluation uses held-out validation data for TensorFlow. For real data add leakage-resistant time splits, baselines, calibration, drift tests, fairness assessment and reproducible model registry.
