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

"""Tests for webhook module."""

import json

from webhook.main import dialogflow_webhook

def test_dialogflow_webhook(mocked_request):

  # Arrange:
  mock_tag = 'MOCK_TAG'
  mock_text = 'MOCK_TEXT'
  request_payload = {'fulfillmentInfo':{}}
  request_payload['fulfillmentInfo']['tag'] = mock_tag
  request_payload['text'] = mock_text
  mocked_request.payload = request_payload

  # Act:
  response_json = dialogflow_webhook(mocked_request)
  response = json.loads(response_json)

  # Assert:
  messages = response['fulfillment_response']['messages']
  assert len(messages) == 1
  message = messages[0]['text']
  assert message['allow_playback_interruption'] == False
  assert message['text'][0] == f'Webhook received: {mock_text} (Tag: {mock_tag})'
