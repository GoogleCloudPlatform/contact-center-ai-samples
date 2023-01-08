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

resource "null_resource" "default_start_flow" {
  # Use a REST API call (instead of Terraform modules) to modify messages and
  # routes in the default start flow and since Dialogflow creates this default
  # start flow automatically
  provisioner "local-exec" {
    command = <<-EOT
    curl --location --request PATCH "https://${self.triggers.LOCATION}-dialogflow.googleapis.com/v3/projects/${self.triggers.PROJECT}/locations/${self.triggers.LOCATION}/agents/${self.triggers.AGENT}/flows/${self.triggers.DEFAULT_START_FLOW}?updateMask=transitionRoutes" \
    -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    -H 'Content-Type: application/json' \
    --data-raw "{
      'transitionRoutes': [{
        'intent': 'projects/${self.triggers.PROJECT}/locations/${self.triggers.LOCATION}/agents/${self.triggers.AGENT}/intents/${self.triggers.DEFAULT_WELCOME_INTENT}',
		    'triggerFulfillment': {
			    'messages': [{
				    'text': {
					    'text': [
						    'Hello, this is a shirt ordering virtual agent. How can I help you?'
					    ]
				    }
			    }]
		    }
      }, {
        'intent': '${self.triggers.STORE_LOCATION_INTENT}',
        'targetPage': '${self.triggers.STORE_LOCATION_PAGE}'
      }, {
        'intent': '${self.triggers.STORE_HOURS_INTENT}',
        'targetPage': '${self.triggers.STORE_HOURS_PAGE}'
      }, {
        'intent': '${self.triggers.NEW_ORDER_INTENT}',
        'targetPage': '${self.triggers.NEW_ORDER_PAGE}'
      }]
    }"
    EOT
  }

  # Use triggers instead of environment variables so that they can be reused in
  # the provisioner to create routes as well as the destroy-time provisioner
  triggers = {
    PROJECT                = var.project_id
    LOCATION               = var.region
    AGENT                  = google_dialogflow_cx_agent.agent.name
    DEFAULT_START_FLOW     = "00000000-0000-0000-0000-000000000000"
    DEFAULT_WELCOME_INTENT = "00000000-0000-0000-0000-000000000000"

    STORE_LOCATION_INTENT = google_dialogflow_cx_intent.store_location.id
    STORE_HOURS_INTENT    = google_dialogflow_cx_intent.store_hours.id
    NEW_ORDER_INTENT      = google_dialogflow_cx_intent.order_new.id

    STORE_LOCATION_PAGE = google_dialogflow_cx_page.store_location.id
    STORE_HOURS_PAGE    = google_dialogflow_cx_page.store_hours.id
    NEW_ORDER_PAGE      = google_dialogflow_cx_page.new_order.id
  }

  # Use a REST API call in a destroy-time provisioner to delete routes in the
  # default start flow since we created them with a REST API call, and Terraform
  # will fail to delete them since they are managed externally
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
    curl --location --request PATCH "https://${self.triggers.LOCATION}-dialogflow.googleapis.com/v3/projects/${self.triggers.PROJECT}/locations/${self.triggers.LOCATION}/agents/${self.triggers.AGENT}/flows/${self.triggers.DEFAULT_START_FLOW}?updateMask=transitionRoutes" \
    -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    -H 'Content-Type: application/json' \
    --data-raw "{
      'transitionRoutes': [{
        'intent': 'projects/${self.triggers.PROJECT}/locations/${self.triggers.LOCATION}/agents/${self.triggers.AGENT}/intents/${self.triggers.DEFAULT_WELCOME_INTENT}',
		    'triggerFulfillment': {
			    'messages': [{
				    'text': {
					    'text': [
						    'Hello, this is a shirt ordering virtual agent. How can I help you?'
					    ]
				    }
			    }]
		    }
      }]
    }"
    EOT
  }

  depends_on = [
    google_dialogflow_cx_agent.agent
  ]
}
