# Terraform starter (not deployed)
Use `terraform init && terraform validate`, then inspect `terraform plan -var='project_id=...' -var='bucket_name=globally-unique-name'`. Provisions a private versioned GCS bucket plus BigQuery dataset only if applied by an authorized operator. No credentials or resources were created in this PR.
