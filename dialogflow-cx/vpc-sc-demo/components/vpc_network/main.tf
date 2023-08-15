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

resource "google_compute_network" "vpc_network" {
  name                    = var.vpc_network
  project                 = var.project_id
  auto_create_subnetworks = false
  depends_on = [
    google_project_service.compute,
  ]
}

resource "google_compute_subnetwork" "reverse_proxy_subnetwork" {
  name                     = var.vpc_subnetwork
  ip_cidr_range            = "10.10.20.0/28"
  project                  = var.project_id
  region                   = var.region
  network                  = google_compute_network.vpc_network.name
  private_ip_google_access = true
}

resource "google_compute_router" "nat_router" {
  name    = "nat-router"
  network = google_compute_network.vpc_network.name
  region  = var.region
}

resource "google_compute_router_nat" "nat_manual" {
  name                               = "nat-config"
  router                             = google_compute_router.nat_router.name
  region                             = google_compute_router.nat_router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  log_config {
    enable = true
    filter = "ALL"
  }
}

resource "google_compute_firewall" "allow_dialogflow" {
  name      = "allow-dialogflow"
  network   = google_compute_network.vpc_network.name
  direction = "INGRESS"
  priority  = 1000
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  source_ranges = ["35.199.192.0/19"]
  target_tags   = ["webhook-reverse-proxy-vm"]
}

resource "google_compute_firewall" "allow" {
  name    = "allow"
  network = google_compute_network.vpc_network.name
  allow {
    protocol = "tcp"
    ports    = ["443", "3389", "22"]
  }
  allow {
    protocol = "icmp"
  }
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_address" "reverse_proxy_address" {
  name         = "webhook-reverse-proxy-address"
  subnetwork   = google_compute_subnetwork.reverse_proxy_subnetwork.id
  address_type = "INTERNAL"
  purpose      = "GCE_ENDPOINT"
  region       = var.region
  address      = var.reverse_proxy_server_ip
}
