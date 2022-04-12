variable "project_id" {
  description = "Required uuid for a test build; links apply and destroy"
  type        = string
}

variable "webhook_function_name" {
  description = "Name of webhook function"
  type        = string
}

variable "webhook_function_entrypoint" {
  description = "Name of webhook function"
  type        = string
}

locals {
	root_dir = abspath("./")
  archive_path = abspath("./tmp/function.zip")
  billing_account = "0145C0-557C58-C970F3"
  org_id = "298490623289"
  region = "us-central1"
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = abspath("./webhook")
  output_path = local.archive_path
}

resource "google_storage_bucket_object" "archive" {
  name   = "index.zip"
  bucket = "ccai-samples-df-tf"
  source = data.archive_file.source.output_path
  depends_on = [data.archive_file.source]
}

resource "google_cloudfunctions_function" "function" {
  project = var.project_id
  name        = var.webhook_function_name
  description = "Basic webhook"
  runtime     = "python39"
  available_memory_mb   = 128
  source_archive_bucket = "ccai-samples-df-tf"
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  timeout               = 60
  entry_point           = var.webhook_function_entrypoint
  region = "us-central1"
  depends_on = [google_storage_bucket_object.archive]
}

# IAM entry for a single user to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name
  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:cloud-function-envoker@${google_cloudfunctions_function.function.project}.iam.gserviceaccount.com"
}
