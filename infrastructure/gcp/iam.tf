resource "google_service_account" "warehouse" {
  account_id = "august-warehouse"
  display_name = "AUGUST dbt warehouse jobs"
}
resource "google_bigquery_dataset_iam_member" "dataset_editor" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role = "roles/bigquery.dataEditor"
  member = "serviceAccount:${google_service_account.warehouse.email}"
}
resource "google_project_iam_member" "job_user" {
  project = var.project_id
  role = "roles/bigquery.jobUser"
  member = "serviceAccount:${google_service_account.warehouse.email}"
}
