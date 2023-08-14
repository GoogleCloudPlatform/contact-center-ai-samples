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

variable "serviceusage_api" {
  type = object({})
}

resource "google_project_service" "run" {
  service                    = "run.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    var.serviceusage_api
  ]
}

resource "google_project_service" "vpcaccess" {
  service                    = "vpcaccess.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    var.serviceusage_api
  ]
}

resource "google_project_service" "appengine" {
  service                    = "appengine.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    var.serviceusage_api
  ]
}
