# AUGUST — dbt historical analytics

**Implemented here:** dbt project and SQL models for standardized raw property events, quality tests and an incremental-history-friendly monthly fact design (full table materialization for deterministic rebuilds). This is SQL **ELT** over a source contract, not a live connection to cloud infrastructure.

Required source table: `raw.property_events(event_id,property_id,occurred_at,amount,event_type)`. The staging SQL rejects negative amounts, missing IDs and unsupported types. The mart aggregates by property, calendar month and event type. Unique event IDs must be enforced upstream. Production pipelines should quarantine rejected rows and audit source freshness.

Run with a valid external `august_analytics` dbt profile and compatible adapter: `dbt build`. The provided model syntax is oriented toward standard SQL warehouses supporting DATE_TRUNC. The user must provision the database/warehouse and credentials separately; Snowflake, BigQuery, Redshift, Azure Fabric, Databricks, Terraform, Kafka, Spark, Airflow and Jenkins are **not deployed** by these files.

This keeps existing fraud inference, econometric models and APIs untouched and avoids introducing fake ML/LLM integration. For a future RAG flow, documents should be isolated in consented object storage, redacted before indexing and evaluated for groundedness and leakage before use.
