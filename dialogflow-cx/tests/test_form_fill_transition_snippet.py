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

"""Dialogflow CX Snippet: Create a cx.Page with a form fulfillment."""

import pytest


@pytest.mark.integration
@pytest.mark.flaky(max_runs=3, reruns_delay=5)
def test_page_with_webhook_fulfillment_snippet(validate_form_sample):
    """Self-testing snippet that demonstrates a page with a form fulfillment."""
    # pylint: disable=C0415,W0404
    import google.cloud.dialogflowcx as cx

    components = cx.WebhooksClient.parse_webhook_path(
        validate_form_sample.webhook_delegator.webhook.name,
    )
    project = components["project"]
    location = components["location"]
    agent = components["agent"]
    webhook = components["webhook"]

    # [START TODO TAG]
    import google.cloud.dialogflowcx as cx

    webhook = (
        f"projects/{project}/locations/{location}/agents/{agent}" f"/webhooks/{webhook}"
    )
    target_page = (
        f"projects/{project}/locations/{location}/agents/{agent}"
        "/flows/00000000-0000-0000-0000-000000000000/pages/START_PAGE"
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
        transition_routes=[
            cx.TransitionRoute(
                condition="$page.params.status = FINAL",
                trigger_fulfillment=cx.Fulfillment(
                    webhook=webhook,
                    tag="validate_form",
                    messages=[
                        cx.ResponseMessage(
                            text=cx.ResponseMessage.Text(text=["Form Filled"])
                        )
                    ],
                ),
                target_page=target_page,
            )
        ],
        form=cx.Form(
            parameters=[
                cx.Form.Parameter(
                    display_name="age",
                    required=True,
                    default_value=None,
                    entity_type="projects/-/locations/-/agents/-/entityTypes/sys.number",
                    fill_behavior=cx.Form.Parameter.FillBehavior(
                        initial_prompt_fulfillment=cx.Fulfillment(
                            messages=[
                                cx.ResponseMessage(
                                    text=cx.ResponseMessage.Text(
                                        text=["How old are you?"],
                                    )
                                )
                            ],
                        )
                    ),
                )
            ]
        ),
    )
    # [END TODO TAG]

    # Update live page:
    page.name = validate_form_sample.page_delegator.page.name
    validate_form_sample.page_delegator.client.update_page(
        request=cx.UpdatePageRequest(
            page=page,
        )
    )
    responses = validate_form_sample.run(["trigger intent", "25"], quiet=True)

    assert responses == [
        {
            "replies": [
                "Entering Example Page",
                "Webhook received: trigger intent (Tag: basic_webhook)",
                "How old are you?",
            ],
            "parameters": {},
        },
        {
            "replies": [
                "Form Filled",
                "Valid age",
            ],
            "parameters": {"age": 25.0},
        },
    ]
