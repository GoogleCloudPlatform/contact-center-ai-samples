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

"""Dialogflow CX Snippet: Create a cx.Page with an entry webhook fulfillment."""

from basic_webhook_sample import BasicWebhookSample
import google.cloud.dialogflowcx as cx
import pytest

# project_id = 'df-terraform-dev'
# webhook_uri = 'https://us-central1-df-terraform-dev.cloudfunctions.net/webhook_fcn_1650336093'
# agent_display_name = 'snippet8'


@pytest.fixture(name="sample", scope="function")
def fixture_sample(session_uuid, project_id, webhook_uri):
    """Test fixture reused for all BasicWebhookSample tests."""
    sample = BasicWebhookSample(
        agent_display_name=f"BasicWebhookSample (test session {session_uuid})",
        project_id=project_id,
        quota_project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.setup()
    yield sample
    sample.tear_down()
    del sample



def test_foo(sample):

  webhook_name = sample.webhook_delegator.webhook.name
  pages_client = sample.page_delegator.client


  # Create a page with a webhook fulfillment:
  # [START TODO TAG]
  page = cx.Page(
    display_name = "FOO",
    entry_fulfillment = cx.Fulfillment(
      messages = [
        cx.ResponseMessage(
          text = cx.ResponseMessage.Text(
            text = ["Entering FOO"]
          )
        )
      ],
      webhook = webhook_name,
      tag = "basic_webhook",
    )
  )
  # [END TODO TAG]


  # Update live page:
  page.name = sample.page_delegator.page.name
  pages_client.update_page(
    request = cx.UpdatePageRequest(
      page=page,
    )
  )
  responses = sample.run(['trigger intent'], quiet=True)


  assert responses == [
    {'replies': [
      'Entering FOO', 
      'Webhook received: trigger intent (Tag: basic_webhook)'
      ], 
      'parameters': {}
    }
  ]
