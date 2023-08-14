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
    google-beta = {
      source  = "hashicorp/google-beta"
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

variable "proxy_server_src" {
  description = "proxy_server_src"
  type        = string
  default     = "./proxy-server-src"
}

resource "google_project_service" "serviceusage" {
  service                    = "serviceusage.googleapis.com"
  project                    = var.project_id
  disable_on_destroy         = false
  disable_dependent_services = true
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

resource "google_project_service" "cloudbuild" {
  service                    = "cloudbuild.googleapis.com"
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

resource "google_project_service" "dialogflow" {
  service                    = "dialogflow.googleapis.com"
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
    google_project_service.iam
  ]
}

resource "google_project_iam_member" "registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  depends_on = [
    google_project_service.iam
  ]
}

resource "google_project_iam_member" "webhook_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  depends_on = [
    google_project_service.iam
  ]
}

data "archive_file" "proxy_server_source" {
  type        = "zip"
  source_dir  = var.proxy_server_src
  output_path = abspath("./tmp/server.zip")
}

resource "google_storage_bucket_object" "proxy_server_source" {
  name   = "server.zip"
  bucket = var.bucket
  source = data.archive_file.proxy_server_source.output_path
  depends_on = [
    var.bucket
  ]
}

resource "google_pubsub_topic" "reverse_proxy_server_build" {
  name = "build"
  depends_on = [
    google_project_service.pubsub,
  ]
}

resource "google_artifact_registry_repository" "webhook_registry" {
  location      = var.region
  repository_id = "webhook-registry"
  format        = "DOCKER"
  project       = var.project_id
  depends_on = [
    google_project_service.artifactregistry,
  ]
}

resource "google_cloudbuild_trigger" "reverse_proxy_server" {

  pubsub_config {
    topic = google_pubsub_topic.reverse_proxy_server_build.id
  }

  build {
    source {
      storage_source {
        bucket = var.bucket
        object = google_storage_bucket_object.proxy_server_source.name
      }
    }

    logs_bucket = "gs://${var.bucket}"

    step {
      name    = "gcr.io/cloud-builders/docker"
      timeout = "120s"
      args    = ["build", "--network", "cloudbuild", "--no-cache", "-t", "${var.region}-docker.pkg.dev/${var.project_id}/webhook-registry/webhook-server-image:latest", "."]
    }
    artifacts {
      images = ["${var.region}-docker.pkg.dev/${var.project_id}/webhook-registry/webhook-server-image:latest"]
    }
  }
  depends_on = [
    google_artifact_registry_repository.webhook_registry,
    var.bucket,
    google_project_service.cloudbuild,
  ]

  provisioner "local-exec" {
    interpreter = [
      "/bin/bash", "-c"
    ]
    command = "source /root/.bashrc && export CLOUDSDK_AUTH_ACCESS_TOKEN=${var.access_token} && gcloud --project=${var.project_id} pubsub topics publish build --message=build"
  }
}

resource "time_sleep" "wait_for_build" {
  create_duration = "60s"
  depends_on = [
    google_cloudbuild_trigger.reverse_proxy_server
  ]
}

resource "google_project_service_identity" "dfsa" {
  provider = google-beta
  project  = var.project_id
  service  = "dialogflow.googleapis.com"
  depends_on = [
    google_project_service.iam,
    google_project_service.dialogflow
  ]
}

resource "google_project_iam_member" "dfsa_sd_viewer" {
  project = var.project_id
  role    = "roles/servicedirectory.viewer"
  member  = "serviceAccount:${google_project_service_identity.dfsa.email}"
}

resource "google_project_iam_member" "dfsa_sd_pscAuthorizedService" {
  project = var.project_id
  role    = "roles/servicedirectory.pscAuthorizedService"
  member  = "serviceAccount:${google_project_service_identity.dfsa.email}"
}

resource "google_service_account" "rpcsa_service_account" {
  account_id   = "rps-sa"
  display_name = "Reverse Proxy Server Service Account"
  depends_on = [
    google_project_service.iam,
  ]
}

resource "google_project_iam_member" "rpcsa_artifactregistry" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.rpcsa_service_account.email}"
}

resource "google_project_iam_member" "rpcsa_cfinvoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.rpcsa_service_account.email}"
}

resource "google_project_iam_member" "rpcsa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.rpcsa_service_account.email}"
}

resource "google_compute_instance" "reverse_proxy_server" {
  name         = "webhook-server"
  project      = var.project_id
  zone         = "${var.region}-a"
  machine_type = "n1-standard-1"
  tags         = ["webhook-reverse-proxy-vm"]
  service_account {
    scopes = [
      "compute-ro",
      "logging-write",
      "monitoring-write",
      "storage-rw",
      "trace",
    ]
    email = google_service_account.rpcsa_service_account.email
  }

  boot_disk {
    auto_delete = true
    device_name = "instance-1"
    mode        = "READ_WRITE"
    initialize_params {
      image = "projects/debian-cloud/global/images/debian-10-buster-v20220719"
      size  = 10
    }
  }

  network_interface {
    network    = var.vpc_network
    subnetwork = var.vpc_subnetwork
    network_ip = var.reverse_proxy_server_ip
  }

  metadata = {
    bucket              = var.bucket
    image               = "${var.region}-docker.pkg.dev/${var.project_id}/webhook-registry/webhook-server-image:latest"
    bot_user            = google_project_service_identity.dfsa.email
    webhook_trigger_uri = "https://${var.region}-${var.project_id}.cloudfunctions.net/${var.webhook_name}"
  }

  metadata_startup_script = file("${path.module}/startup_script.sh")

  provisioner "local-exec" {
    interpreter = [
      "/bin/bash", "-c"
    ]
    command = "source /root/.bashrc && /app/wait_until_server_ready.sh --zone=${self.zone} --project_id=${var.project_id}  --token=${var.access_token}"
  }
  depends_on = [
    time_sleep.wait_for_build,
    var.bucket,
    google_project_iam_member.dfsa_sd_viewer,
    google_project_iam_member.dfsa_sd_pscAuthorizedService,
    google_project_iam_member.rpcsa_artifactregistry,
    google_project_iam_member.rpcsa_cfinvoker,
    google_project_iam_member.rpcsa_storage_admin,
  ]
}
