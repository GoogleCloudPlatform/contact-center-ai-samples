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

terraform {
    required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.77.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 4.77.0"
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

resource "google_project_service" "serviceusage" {
  service                    = "serviceusage.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
}

resource "google_project_service" "servicedirectory" {
  service                    = "servicedirectory.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

variable "vpc_network" {
  description = "VPC Network"
  type        = string
  default     = "webhook-net"
}

variable "service_directory_namespace" {
  description = "Service Directory Namespace"
  type        = string
  default     = "df-namespace"
}

variable "service_directory_service" {
  description = "Service Directory Service"
  type        = string
  default     = "df-service"
}

variable "service_directory_endpoint" {
  description = "Service Directory Endpoint"
  type        = string
  default     = "df-endpoint"
}

variable "reverse_proxy_server_ip" {
  description = "reverse_proxy_server_ip"
  type        = string
  default     = "10.10.20.2"
}

data "google_project" "project" {
  project_id = var.project_id
}

resource "google_service_directory_namespace" "reverse_proxy" {
  provider     = google-beta
  namespace_id = var.service_directory_namespace
  location     = var.region
  project      = var.project_id
  depends_on = [
    google_project_service.servicedirectory
  ]
}

resource "google_service_directory_service" "reverse_proxy" {
  provider   = google-beta
  service_id = var.service_directory_service
  namespace  = google_service_directory_namespace.reverse_proxy.id
}

resource "google_service_directory_endpoint" "reverse_proxy" {
  provider    = google-beta
  endpoint_id = var.service_directory_endpoint
  service     = google_service_directory_service.reverse_proxy.id
  metadata = {
    stage  = "prod"
    region = var.region
  }
  network = "projects/${data.google_project.project.number}/locations/global/networks/${var.vpc_network}"
  address = var.reverse_proxy_server_ip
  port    = 443
}
