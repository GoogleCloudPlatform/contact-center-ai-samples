variable "project_id" {
  description = "Required uuid for a test build; links apply and destroy"
  type        = string
}

variable "basic_webhook_function_name" {
  description = "Name of webhook function"
  type        = string
}

variable "build_uuid" {
  description = "Required uuid for a test build; links apply and destroy"
  type        = string
}

locals {
	root_dir = abspath("./")
  archive_path = abspath("./tmp/function-${var.build_uuid}.zip")
  billing_account = "0145C0-557C58-C970F3"
  org_id = "298490623289"
  region = "us-central1"
}

resource "google_project_iam_binding" "project" {
  project = var.project_id
  role    = "roles/editor"

  members = [
    "user:nicholascain@google.com",
    "user:aribray@google.com",
  ]
}

resource "google_project_service" "service" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "eventarc.googleapis.com",
    "run.googleapis.com",
    "dialogflow.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
  ])
  service = each.key
  project            = var.project_id
  disable_on_destroy = true
  disable_dependent_services = true
}

resource "google_storage_bucket" "bucket" {
  project = var.project_id
  name     = "ccai-samples-df-tf-${var.build_uuid}"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
  depends_on = [google_project_service.service]
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = abspath("./basic_webhook")
  output_path = local.archive_path
}

resource "google_storage_bucket_object" "archive" {
  name   = "index.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.source.output_path
  depends_on = [google_storage_bucket.bucket, data.archive_file.source]
}

resource "google_cloudfunctions_function" "function" {
  project = var.project_id
  name        = var.basic_webhook_function_name
  description = "Basic webhook"
  runtime     = "python39"
  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  timeout               = 60
  entry_point           = var.basic_webhook_function_name
  region = "us-central1"
  depends_on = [google_project_service.service, google_storage_bucket_object.archive]
}

resource "google_service_account" "sa" {
  account_id   = "sa-${var.build_uuid}"
  display_name = "sa-${var.build_uuid}"
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

resource "google_service_account" "oidc_sa" {
  project    = var.project_id
  account_id = "oidc-sa-df"
}

resource "google_project_iam_member" "project" {
  project = var.project_id
  role    = "roles/dialogflow.admin"
  member  = "serviceAccount:${google_service_account.oidc_sa.email}"
}

module "github-actions-runners" {
  source  = "terraform-google-modules/github-actions-runners/google"
  version = "3.0.0"
}

module "gh_oidc" {
  source      = "./.terraform/modules/github-actions-runners/modules/gh-oidc"
  project_id  = var.project_id
  pool_id     = "gh-pool-df"
  provider_id = "gh-provider-df"
  sa_mapping = {
    (google_service_account.oidc_sa.account_id) = {
      sa_name   = google_service_account.oidc_sa.name
      attribute = "attribute.repository/nicain/contact-center-ai-samples"
    }
  }
}
