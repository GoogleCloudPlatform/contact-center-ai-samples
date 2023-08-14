# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.77.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4.0"
    }
  }
  required_version = ">= 1.2.0"
}

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
  archive_path = abspath("./tmp/function.zip")
  region       = "us-central1"
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = abspath("./webhook")
  output_path = local.archive_path
}

resource "google_storage_bucket_object" "archive" {
  name       = "index.zip"
  bucket     = "ccai-samples-df-tf"
  source     = data.archive_file.source.output_path
  depends_on = [data.archive_file.source]
}

resource "google_cloudfunctions_function" "function" {
  project               = var.project_id
  name                  = var.webhook_function_name
  description           = "Basic webhook"
  runtime               = "python39"
  available_memory_mb   = 128
  source_archive_bucket = "ccai-samples-df-tf"
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  timeout               = 60
  entry_point           = var.webhook_function_entrypoint
  region                = local.region
  depends_on            = [google_storage_bucket_object.archive]
}

# IAM entry for a single user to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:cloud-function-envoker@${google_cloudfunctions_function.function.project}.iam.gserviceaccount.com"
}
