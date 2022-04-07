variable "build_uuid" {
  description = "Required uuid for a test build; links apply and destroy"
  type        = string
}

locals {
  build_project_id = "nicholascain-starter-project"
  test_project_id = "nicholascain-starter-project"
	root_dir = abspath("./")
  archive_path = abspath("./tmp/function-${var.build_uuid}.zip")
}

resource "google_storage_bucket" "bucket" {
  project = local.build_project_id
  name     = "contact-center-ai-samples-temp-bucket-${var.build_uuid}"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = abspath("./webhook")
  output_path = local.archive_path
}

resource "google_storage_bucket_object" "archive" {
  name   = "index.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.source.output_path
}

resource "google_cloudfunctions_function" "function" {
  project = local.test_project_id
  name        = "webhook-test-${var.build_uuid}"
  description = "Webhook"
  runtime     = "python39"
  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  timeout               = 60
  entry_point           = "dialogflow_webhook"
  region = "us-central1"
}

resource "google_service_account" "sa" {
  account_id   = "invoker-${var.build_uuid}"
  display_name = "invoker-${var.build_uuid}"
  project      = google_cloudfunctions_function.function.project
}

# IAM entry for a single user to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name
  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${google_service_account.sa.display_name}@${google_cloudfunctions_function.function.project}.iam.gserviceaccount.com"
}