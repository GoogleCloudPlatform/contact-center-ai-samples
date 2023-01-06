# Copyright 2023 Google LLC
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

resource "google_dialogflow_cx_page" "store_location" {
  parent       = google_dialogflow_cx_agent.agent.start_flow
  display_name = "Store Location"

  entry_fulfillment {
    return_partial_responses = false

    messages {
      text {
        text = [
          "Our store is located at 1007 Mountain Drive, Gotham City, NJ.",
        ]
      }
    }
  }
}

resource "google_dialogflow_cx_page" "store_hours" {
  parent       = google_dialogflow_cx_agent.agent.start_flow
  display_name = "Store Hours"

  entry_fulfillment {
    return_partial_responses = false

    messages {
      text {
        text = [
          "We are open from 8 am to 5 pm Monday through Sunday.",
        ]
      }
    }
  }
}

resource "google_dialogflow_cx_page" "new_order" {
  parent       = google_dialogflow_cx_agent.agent.start_flow
  display_name = "New Order"

  form {
    parameters {
      display_name = "color"
      entity_type  = "projects/-/locations/-/agents/-/entityTypes/sys.color"
      is_list      = false
      redact       = false
      required     = true

      fill_behavior {
        initial_prompt_fulfillment {
          return_partial_responses = false

          messages {
            text {
              text = [
                "What color would you like?",
              ]
            }
          }
        }
      }
    }
    parameters {
      display_name = "size"
      entity_type  = google_dialogflow_cx_entity_type.size.id
      is_list      = false
      redact       = false
      required     = true

      fill_behavior {
        initial_prompt_fulfillment {
          return_partial_responses = false

          messages {
            text {
              text = [
                "What size do you want?",
              ]
            }
          }
        }
      }
    }
  }

  transition_routes {
    condition   = "$page.params.status = \"FINAL\""
    target_page = google_dialogflow_cx_page.order_confirmation.id

    trigger_fulfillment {
      return_partial_responses = false

      messages {
        text {
          text = [
            "You have selected a $session.params.size, $session.params.color shirt.",
          ]
        }
      }
    }
  }
  transition_routes {
    condition = "true"

    trigger_fulfillment {
      return_partial_responses = false

      messages {
        text {
          text = [
            "I'd like to collect a bit more information from you.",
          ]
        }
      }
    }
  }
}

resource "google_dialogflow_cx_page" "order_confirmation" {
  parent       = google_dialogflow_cx_agent.agent.start_flow
  display_name = "Order Confirmation"

  entry_fulfillment {
    return_partial_responses = false

    messages {
      text {
        text = [
          "You can pick up your order for a $session.params.size $session.params.color shirt in 7 to 10 business days. Goodbye.",
        ]
      }
    }
  }

  transition_routes {
    condition   = "true"
    target_page = "${google_dialogflow_cx_agent.agent.start_flow}/pages/END_SESSION"
  }

}
