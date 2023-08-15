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
    time = {
      source  = "hashicorp/time"
      version = ">= 0.9.1"
    }
  }
  required_version = ">= 1.2.0"
}

variable "project_id" {
  description = "Project ID"
  type        = string
}

variable "region" {
  description = "Region"
  type        = string
}

variable "access_token" {
  description = "Access Token"
  type        = string
  sensitive   = true
}

variable "webhook_src" {
  description = "webhook_src"
  type        = string
}

variable "webhook_name" {
  description = "webhook_name"
  type        = string
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

variable "agent_display_name" {
  description = "Agent Display Name"
  type        = string
  default     = "Telecommunications"
}

variable "dialogflow_api" {
  type = object({})
}

variable "cloudfunctions_api" {
  type = object({})
}

variable "cloudbuild_api" {
  type = object({})
}

variable "bucket" {
  type = object({})
}

variable "bucket_name" {
  description = "bucket_name"
  type        = string
}

data "archive_file" "webhook_source" {
  type        = "zip"
  source_dir  = var.webhook_src
  output_path = abspath("./tmp/webhook.zip")
}

resource "google_storage_bucket_object" "webhook" {
  name   = "webhook.zip"
  bucket = var.bucket_name
  source = data.archive_file.webhook_source.output_path
  depends_on = [
    var.bucket
  ]
}

resource "time_sleep" "wait_for_apis" {
  create_duration = "20s"
  depends_on = [
    var.cloudfunctions_api,
    var.cloudbuild_api,
    var.dialogflow_api,
  ]
}

resource "google_cloudfunctions_function" "webhook" {
  project               = var.project_id
  name                  = var.webhook_name
  description           = "VPC-SC Demo Webhook"
  runtime               = var.webhook_runtime
  available_memory_mb   = 128
  source_archive_bucket = var.bucket_name
  source_archive_object = google_storage_bucket_object.webhook.name
  trigger_http          = true
  timeout               = 60
  entry_point           = var.webhook_entrypoint
  region                = var.region
  ingress_settings      = var.webhook_ingress_setting
  depends_on = [
    time_sleep.wait_for_apis,
    var.bucket,
  ]
}

resource "google_dialogflow_cx_agent" "full_agent" {
  display_name            = var.agent_display_name
  location                = var.region
  default_language_code   = "en"
  time_zone               = "America/Chicago"
  project                 = var.project_id
  enable_spell_correction = true

  provisioner "local-exec" {
    interpreter = [
      "/bin/bash", "-c"
    ]
    command = "source /root/.bashrc && /deploy/terraform/webhook-agent/deploy_agent.sh --region=${var.region} --project_id=${var.project_id} --webhook_name=${var.webhook_name} --token=${var.access_token}"
  }

  depends_on = [
    time_sleep.wait_for_apis,
    google_cloudfunctions_function.webhook,
  ]
}
