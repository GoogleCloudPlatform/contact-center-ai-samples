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
  }
  required_version = ">= 1.2.0"
}

variable "project_id" {
  description = "Project ID"
  type        = string
}

variable "service_perimeter" {
  description = "Service Perimeter"
  type        = string
  default     = "df_webhook"
}

variable "access_policy_name" {
  description = "Access Policy Name"
  type        = string
}

variable "accesscontextmanager_api" {
  type = object({})
}

variable "cloudbilling_api" {
  type = object({})
}

data "google_project" "project" {
  project_id = var.project_id
}

resource "google_access_context_manager_service_perimeter" "service_perimeter" {
  count  = var.access_policy_name == "null" ? 0 : 1
  parent = var.access_policy_name
  name   = "${var.access_policy_name}/servicePerimeters/${var.service_perimeter}"
  title  = var.service_perimeter
  status {
    resources = [
      "projects/${data.google_project.project.number}",
    ]
    restricted_services = []
  }
  depends_on = [
    var.accesscontextmanager_api,
    var.cloudbilling_api,
  ]
}
