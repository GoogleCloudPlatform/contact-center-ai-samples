resource "google_dialogflow_cx_entity_type" "size" {
  parent       = google_dialogflow_cx_agent.agent.id
  display_name = "size"
  kind         = "KIND_MAP"

  entities {
    value    = "small"
    synonyms = ["little", "small", "tiny"]
  }

  entities {
    value    = "medium"
    synonyms = ["medium", "regular", "average"]
  }

  entities {
    value    = "large"
    synonyms = ["big", "giant", "large"]
  }
}
