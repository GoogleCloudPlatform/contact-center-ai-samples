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
  sensitive = true
}

variable "webhook_src" {
  description = "webhook_src"
  type        = string
}

variable "webhook_name" {
  description = "webhook_name"
  type        = string
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
  create_duration = "60s"
  depends_on = [
    var.cloudfunctions_api,
    var.cloudbuild_api
  ]
}

resource "google_cloudfunctions_function" "webhook" {
  project = var.project_id
  name        = var.webhook_name
  description = "VPC-SC Demo Webhook"
  runtime     = "python39"
  available_memory_mb   = 128
  source_archive_bucket = var.bucket_name
  source_archive_object = google_storage_bucket_object.webhook.name
  trigger_http          = true
  timeout               = 60
  entry_point           = "cxPrebuiltAgentsTelecom"
  region = var.region
  ingress_settings = "ALLOW_ALL"
  depends_on = [
    time_sleep.wait_for_apis,
    var.bucket
  ]
}

resource "google_dialogflow_cx_agent" "full_agent" {
  display_name = "Telecommunications"
  location = var.region
  default_language_code = "en"
  time_zone = "America/Chicago"
  project = var.project_id
  enable_spell_correction = true

  provisioner "local-exec" {
    command = "/deploy/terraform/webhook-agent/deploy_agent.sh --region=${var.region} --project_id=${var.project_id} --webhook_name=${var.webhook_name} --token=${var.access_token}"
  }
  depends_on = [
    var.dialogflow_api,
    google_cloudfunctions_function.webhook,
  ]
}