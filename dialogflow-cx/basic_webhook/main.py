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

"""main.py creates a sample webhook handler for Dialogflow CX"""

'''
export TERRAFORM_BASIC_WEBHOOK_FUNCTION_NAME=basic_dialogflow_webhook
'''

import json


def basic_dialogflow_webhook(request):
    '''main handles a Dialogflow CX webhook request'''
    request_dict = request.get_json()
    tag = request_dict["fulfillmentInfo"]["tag"]
    user_query = request_dict["text"]
    return json.dumps(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"Webhook received: {user_query} (Tag: {tag})"],
                            "allow_playback_interruption": False,
                        }
                    }
                ]
            }
        }
    )

def build_request_dict(tag, text):
  request_mapping = {'fulfillmentInfo':{}}
  request_mapping['fulfillmentInfo']['tag'] = tag
  request_mapping['text'] = text
  return request_mapping


def extract_text(response_json: str, message_index=0):
  response = json.loads(response_json)
  messages = response['fulfillment_response']['messages']
  return messages[message_index]['text']['text'][0]
