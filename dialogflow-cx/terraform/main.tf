locals {
  project_name = "df-terraform-dev"
	root_dir = abspath("./")
  archive_path = abspath("./tmp/function-${random_id.id.hex}.zip")
  billing_account = "0145C0-557C58-C970F3"
  org_id = "298490623289"
  region = "us-central1"
}

resource "random_id" "id" {
  byte_length = 2
  prefix      = local.project_name
}

resource "google_project" "project" {
  name            = random_id.id.hex
  project_id      = random_id.id.hex
  billing_account = local.billing_account
  org_id          = local.org_id
}

resource "google_project_service" "service" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "eventarc.googleapis.com",
    "run.googleapis.com",
    "dialogflow.googleapis.com",
  ])
  service = each.key
  project            = google_project.project.project_id
  disable_on_destroy = true
  disable_dependent_services = true
}

resource "google_storage_bucket" "bucket" {
  project = google_project.project.project_id
  name     = "temp-${random_id.id.hex}"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
  depends_on = [google_project_service.service]
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
  depends_on = [google_storage_bucket.bucket, data.archive_file.source]
}

resource "google_cloudfunctions_function" "function" {
  project = google_project.project.project_id
  name        = "wh-${random_id.id.hex}"
  description = "Webhook"
  runtime     = "python39"
  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  timeout               = 60
  entry_point           = "dialogflow_webhook"
  region = "us-central1"
  depends_on = [google_project_service.service, google_storage_bucket_object.archive]
}

resource "google_service_account" "sa" {
  account_id   = "sa-${random_id.id.hex}"
  display_name = "sa-${random_id.id.hex}"
  project      = google_cloudfunctions_function.function.project
}

# IAM entry for a single user to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name
  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${google_service_account.sa.display_name}@${google_cloudfunctions_function.function.project}.iam.gserviceaccount.com"
  depends_on = [google_service_account.sa]
}