resource "google_dialogflow_cx_agent" "agent" {
  display_name          = "shirt-ordering-agent"
  location              = var.region
  default_language_code = "en"
  time_zone             = "America/Chicago"
}
