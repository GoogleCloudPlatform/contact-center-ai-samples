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

variable "region" {
  description = "Region"
  type        = string
}

variable "bucket" {
  description = "bucket"
  type        = string
}

variable "vpc_network" {
  description = "VPC Network Name"
  type        = string
  default     = "webhook-net"
}

variable "vpc_subnetwork" {
  description = "Subnetwork for Reverse Proxy Server"
  type        = string
  default     = "webhook-subnet"
}

variable "reverse_proxy_server_ip" {
  description = "IP Address of Reverse Proxy Servier"
  type        = string
  default     = "10.10.20.2"
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

variable "webhook_src" {
  description = "webhook_src"
  type        = string
  default     = "/components/telecom-webhook-src"
}

variable "proxy_server_src" {
  description = "proxy_server_src"
  type        = string
  default     = "/components/proxy-server-src"
}

variable "service_perimeter" {
  description = "Service Perimeter"
  type        = string
  default     = "df_webhook"
}

variable "access_policy_name" {
  description = "Access Policy"
  default     = "null"
  type        = string
}

variable "webhook_name" {
  description = "webhook_name"
  type        = string
  default     = "custom-telco-webhook"
}

provider "google" {
  project               = var.project_id
  billing_project       = var.project_id
  region                = var.region
  user_project_override = true
}

terraform {
    required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.77.0"
    }
  }
  #START_BACKEND
  backend "gcs" {
    bucket = null
    prefix = null
  }
  #END_BACKEND
  required_version = ">= 1.2.0"
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

resource "google_project_service" "compute" {
  service                    = "compute.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

data "google_project" "project" {
  project_id = var.project_id
}

resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  depends_on = [
    google_project_service.compute
  ]
}

resource "google_project_iam_member" "registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  depends_on = [
    google_project_service.compute
  ]
}

resource "google_project_iam_member" "webhook_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  depends_on = [
    google_project_service.compute
  ]
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

resource "google_project_service" "accesscontextmanager" {
  service                    = "accesscontextmanager.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

resource "google_project_service" "cloudbilling" {
  service                    = "cloudbilling.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

resource "google_project_service" "iam" {
  service                    = "iam.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

resource "google_project_service" "artifactregistry" {
  service                    = "artifactregistry.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}



resource "google_project_service" "pubsub" {
  service                    = "pubsub.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on = [
    google_project_service.serviceusage
  ]
}

resource "google_storage_bucket" "bucket" {
  name                        = var.bucket
  location                    = "US"
  project                     = var.project_id
  force_destroy               = true
  uniform_bucket_level_access = true
}

module "services" {
  source           = "/deploy/terraform/services"
  project_id       = var.project_id
  serviceusage_api = google_project_service.serviceusage
  depends_on = [
    google_project_service.servicedirectory,
    google_project_service.compute,
    google_project_service.dialogflow,
    google_project_service.cloudfunctions,
    google_project_service.cloudbuild,
    google_project_service.accesscontextmanager,
    google_project_service.iam,
    google_project_service.cloudbilling,
    google_project_service.artifactregistry,
    google_project_service.serviceusage,
    google_project_service.pubsub,
  ]
}

module "vpc_network" {
  source                    = "/deploy/terraform/vpc-network"
  project_id                = var.project_id
  region                    = var.region
  vpc_network               = var.vpc_network
  vpc_subnetwork            = var.vpc_subnetwork
  reverse_proxy_server_ip   = var.reverse_proxy_server_ip
  proxy_permission_storage  = google_project_iam_member.storage_admin
  proxy_permission_registry = google_project_iam_member.registry_reader
  proxy_permission_invoke   = google_project_iam_member.webhook_invoker
  iam_api                   = google_project_service.iam
  dialogflow_api            = google_project_service.dialogflow
  artifactregistry_api      = google_project_service.artifactregistry
  pubsub_api                = google_project_service.pubsub
  cloudbuild_api            = google_project_service.cloudbuild
  compute_api               = google_project_service.compute
  proxy_server_src          = var.proxy_server_src
  access_token              = var.access_token
  bucket                    = google_storage_bucket.bucket
  bucket_name               = google_storage_bucket.bucket.name
  webhook_name              = var.webhook_name
}

module "service_directory" {
  source                        = "/deploy/terraform/service-directory"
  project_id                    = var.project_id
  region                        = var.region
  vpc_network                   = var.vpc_network
  reverse_proxy_server_ip       = var.reverse_proxy_server_ip
  service_directory_endpoint    = var.service_directory_endpoint
  service_directory_service     = var.service_directory_service
  service_directory_namespace   = var.service_directory_namespace
  service_directory_service_api = google_project_service.servicedirectory
}

module "webhook_agent" {
  source             = "/deploy/terraform/webhook-agent"
  project_id         = var.project_id
  region             = var.region
  access_token       = var.access_token
  webhook_src        = var.webhook_src
  webhook_name       = var.webhook_name
  bucket             = google_storage_bucket.bucket
  bucket_name        = google_storage_bucket.bucket.name
  dialogflow_api     = google_project_service.dialogflow
  cloudfunctions_api = google_project_service.cloudfunctions
  cloudbuild_api     = google_project_service.cloudbuild
}

module "service_perimeter" {
  source                   = "/deploy/terraform/service-perimeter"
  project_id               = var.project_id
  service_perimeter        = var.service_perimeter
  accesscontextmanager_api = google_project_service.accesscontextmanager
  access_policy_name       = var.access_policy_name
  cloudbilling_api         = google_project_service.cloudbilling
}
