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

variable "access_token" {
  description = "Access Token"
  type        = string
  sensitive   = true
}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.77.0"
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

provider "google" {
  project               = var.project_id
  billing_project       = var.project_id
  region                = var.region
  user_project_override = true
}

variable "webhook_name" {
  description = "webhook_name"
  type        = string
  default     = "custom-telco-webhook"
}

variable "agent_display_name" {
  description = "Agent Display Name"
  type        = string
  default     = "Telecommunications"
}

resource "google_project_service" "serviceusage" {
  service                    = "serviceusage.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
}

resource "google_project_service" "dialogflow" {
  service                    = "dialogflow.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

resource "time_sleep" "wait_for_apis" {
  create_duration = "60s"
  depends_on = [
    google_project_service.dialogflow,
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
    command = "source /root/.bashrc && /app/provision_agent.sh --region=${var.region} --project_id=${var.project_id} --webhook_name=${var.webhook_name} --token=${var.access_token}"
  }

  depends_on = [
    time_sleep.wait_for_apis,
  ]
}
