# Integration status and deployment instructions

The files added in this branch are **environment-ready examples**, not claims of active deployed infrastructure. Cloud integrations require credentials, billing and controlled provisioning.

## GCP
Set up an authorized Google Cloud project, enable BigQuery and Cloud Storage, and authenticate using workload identity federation (recommended) rather than permanent keys. From `infrastructure/gcp`, run `terraform init`, `terraform validate`, then review `terraform plan -var=project_id=PROJECT -var=bucket_name=UNIQUE_NAME`. Applying the plan creates billed resources; nothing is applied automatically. Dataset access is isolated via dedicated service accounts.

## Security / DevSecOps
CI validates Terraform syntax, Python where applicable and Kubernetes manifests. Security scans and project-specific CI remain required gates. Review image digests, SBOM, dependency vulnerabilities, secret scanning, OIDC/IAM boundaries, network egress, data retention and audit logging prior to deployment. A passing static validation does **not** assert integration, privacy or operational readiness.

## Real-time
Kafka consumer examples are opt-in and require actual brokers plus durable DLQ/replay configuration. Verify ordering, outbox atomicity, backpressure, idempotency, checkpoints, monitoring and alerting before production use. No live service was provisioned.

## Warehouses and RAG
AUGUST includes `infrastructure/warehouse/dbt_profiles.example.yml`; copy it **outside version control** as `profiles.yml` after setting provider environment variables. Configure the correct adapter and target, create/permission the source schema and run `dbt build --target bigquery|snowflake|databricks`. SQL schemas are templates; Snowflake and Databricks are not provisioned automatically. `GroundedAgent` is deterministic retrieval with an optional caller-supplied generator, not a hosted LLM or autonomous tools runtime. Add authentication, prompt-injection isolation, redaction, evaluation and provider credentials before any remote LLM use.
