provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

terraform {
  required_providers {
    google = ">= 4.40.0"
    null = ">= 3.2.0"
  }
}
