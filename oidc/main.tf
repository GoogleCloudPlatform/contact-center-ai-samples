variable "project_id" {
  description = "Required uuid for a test build; links apply and destroy"
  type        = string
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

resource "google_project_iam_binding" "project" {
  project = var.project_id
  role    = "roles/editor"

  members = [
    "user:nicholascain@google.com",
    "user:aribray@google.com",
  ]
}

resource "google_storage_bucket" "bucket" {
  project = var.project_id
  name     = "ccai-samples-df-tf"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_service_account" "oidc_sa" {
  project    = var.project_id
  account_id = "oidc-sa-df-3"
}

resource "google_project_iam_member" "project" {
  project = var.project_id
  role    = "roles/dialogflow.admin"
  member  = "serviceAccount:${google_service_account.oidc_sa.email}"
}

resource "google_project_iam_member" "storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.oidc_sa.email}"
}

resource "google_project_iam_member" "cloudfunctions_admin" {
  project = var.project_id
  role    = "roles/cloudfunctions.admin"
  member  = "serviceAccount:${google_service_account.oidc_sa.email}"
}

resource "google_project_iam_member" "serviceAccountAdmin" {
  project = var.project_id
  role    = "roles/iam.serviceAccountAdmin"
  member  = "serviceAccount:${google_service_account.oidc_sa.email}"
}

module "github-actions-runners" {
  source  = "terraform-google-modules/github-actions-runners/google"
  version = "3.0.0"
}

module "gh_oidc" {
  source      = "./.terraform/modules/github-actions-runners/modules/gh-oidc"
  project_id  = var.project_id
  pool_id     = "gh-pool-df-3"
  provider_id = "gh-provider-df-3"
  sa_mapping = {
    (google_service_account.oidc_sa.account_id) = {
      sa_name   = google_service_account.oidc_sa.name
      attribute = "attribute.repository/nicain/contact-center-ai-samples"
    }
  }
}

resource "google_service_account" "function_envoker" {
  account_id   = "cloud-function-envoker"
  display_name = "cloud-function-envoker"
  project      = var.project_id
}