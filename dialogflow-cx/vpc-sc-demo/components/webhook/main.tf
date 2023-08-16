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

variable "project_id" {
  description = "Project ID"
  type        = string
}

variable "bucket" {
  description = "bucket"
  type        = string
}

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
    time = {
      source  = "hashicorp/time"
      version = ">= 0.9.1"
    }
  }
  backend "gcs" {
    bucket = null
    prefix = null
  }
  required_version = ">= 1.2.0"
}

variable "region" {
  description = "Region"
  type        = string
  default     = "us-central1"
}

variable "webhook_src" {
  description = "webhook_src"
  type        = string
  default     = "./telecom-webhook-src"
}

variable "webhook_name" {
  description = "webhook_name"
  type        = string
  default     = "custom-telco-webhook"
}

variable "webhook_obj_name" {
  description = "Blob name of webhook zip file in GCS bucket"
  type        = string
  default     = "webhook.zip"
}

variable "webhook_runtime" {
  description = "Webhook runtime"
  type        = string
  default     = "python39"
}

variable "webhook_entrypoint" {
  description = "Webhook entrypoint"
  type        = string
  default     = "cx_prebuilt_agents_telecom"
}

variable "webhook_ingress_setting" {
  description = "Webhook ingress setting"
  type        = string
  default     = "ALLOW_ALL"
}

resource "google_project_service" "serviceusage" {
  service                    = "serviceusage.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
}

resource "google_project_service" "cloudfunctions" {
  service                    = "cloudfunctions.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

resource "google_project_service" "cloudbuild" {
  service                    = "cloudbuild.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

data "archive_file" "webhook_source" {
  type        = "zip"
  source_dir  = var.webhook_src
  output_path = abspath("./tmp/webhook.zip")
}

resource "google_storage_bucket_object" "webhook" {
  name   = var.webhook_obj_name
  bucket = var.bucket
  source = data.archive_file.webhook_source.output_path
}

resource "time_sleep" "wait_for_apis" {
  create_duration = "60s"
  depends_on = [
    google_project_service.cloudfunctions,
    google_project_service.cloudbuild,
  ]
}

resource "google_cloudfunctions_function" "webhook" {
  project               = var.project_id
  name                  = var.webhook_name
  description           = "VPC-SC Demo Webhook"
  runtime               = var.webhook_runtime
  available_memory_mb   = 128
  source_archive_bucket = var.bucket
  source_archive_object = google_storage_bucket_object.webhook.name
  trigger_http          = true
  timeout               = 60
  entry_point           = var.webhook_entrypoint
  region                = var.region
  ingress_settings      = var.webhook_ingress_setting
  depends_on = [
    time_sleep.wait_for_apis
  ]
}
