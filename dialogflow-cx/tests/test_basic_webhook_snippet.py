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


def test_page_with_webhook_fulfillment_snippet(basic_webhook_sample):
    """Self-testing snippet that demonstrates a page with a webhook fulfillment."""
    # pylint: disable=C0415,W0404
    import google.cloud.dialogflowcx as cx

    components = cx.WebhooksClient.parse_webhook_path(
        basic_webhook_sample.webhook_delegator.webhook.name,
    )
    project = components["project"]
    location = components["location"]
    agent = components["agent"]
    webhook = components["webhook"]

    # [START TODO TAG]
    import google.cloud.dialogflowcx as cx

    webhook = (
        f"projects/{project}/locations/{location}/agents/{agent}/webhooks/{webhook}"
    )

    page = cx.Page(
        display_name="Example Page",
        entry_fulfillment=cx.Fulfillment(
            messages=[
                cx.ResponseMessage(
                    text=cx.ResponseMessage.Text(text=["Entering Example Page"])
                )
            ],
            webhook=webhook,
            tag="basic_webhook",
        ),
    )
    # [END TODO TAG]

    # Update live page:
    page.name = basic_webhook_sample.page_delegator.page.name
    basic_webhook_sample.page_delegator.client.update_page(
        request=cx.UpdatePageRequest(
            page=page,
        )
    )
    responses = basic_webhook_sample.run(["trigger intent"], quiet=True)

    assert responses == [
        {
            "replies": [
                "Entering Example Page",
                "Webhook received: trigger intent (Tag: basic_webhook)",
            ],
            "parameters": {},
        }
    ]
