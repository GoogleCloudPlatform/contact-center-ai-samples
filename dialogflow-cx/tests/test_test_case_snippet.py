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

"""Dialogflow CX Snippet: Create a cx.TestCase."""

import pytest


@pytest.mark.integration
@pytest.mark.flaky(max_runs=3, reruns_delay=5)
def test_page_with_webhook_fulfillment_snippet(basic_webhook_sample):
    """Self-testing snippet that demonstrates creating a cx.TestVase."""
    # pylint: disable=C0415,W0404,R0914
    import google.cloud.dialogflowcx as cx

    intent_components = cx.IntentsClient.parse_intent_path(
        basic_webhook_sample.intent_delegator.intent.name
    )
    project = intent_components["project"]
    location = intent_components["location"]
    agent = intent_components["agent"]
    intent = intent_components["intent"]
    page_components = cx.PagesClient.parse_page_path(
        basic_webhook_sample.page_delegator.page.name
    )
    page = page_components["page"]
    flow = page_components["flow"]

    test_cases_client = basic_webhook_sample.test_cases_client

    # [START TODO TAG]
    import time

    import google.cloud.dialogflowcx as cx

    parent = f"projects/{project}/locations/{location}/agents/{agent}"
    current_page_name = (
        f"projects/{project}/locations/{location}/agents/{agent}"
        f"/flows/{flow}/pages/{page}"
    )
    triggered_intent_name = (
        f"projects/{project}/locations/{location}/agents/{agent}/intents/{intent}"
    )
    flow = f"projects/{project}/locations/{location}/agents/{agent}/flows/{flow}"

    agent_response_list = (
        [
            "Entering Main Page",
            "Webhook received: trigger intent (Tag: basic_webhook)",
        ],
    )
    is_webhook_enabled = True
    user_input = "trigger intent"

    test_case = test_cases_client.create_test_case(
        parent=parent,
        test_case=cx.TestCase(
            display_name="Test Case",
            test_case_conversation_turns=[
                cx.ConversationTurn(
                    virtual_agent_output=cx.ConversationTurn.VirtualAgentOutput(
                        current_page=cx.Page(name=current_page_name),
                        triggered_intent=cx.Intent(name=triggered_intent_name),
                        text_responses=[
                            cx.ResponseMessage.Text(text=text)
                            for text in agent_response_list
                        ],
                    ),
                    user_input=cx.ConversationTurn.UserInput(
                        is_webhook_enabled=is_webhook_enabled,
                        input=cx.QueryInput(
                            text=cx.TextInput(
                                text=user_input,
                            )
                        ),
                    ),
                )
            ],
            test_config=cx.TestConfig(flow=flow),
        ),
    )

    lro = test_cases_client.run_test_case(
        request=cx.RunTestCaseRequest(name=test_case.name)
    )
    while lro.running():
        time.sleep(0.1)
    result = lro.result().result

    assert result.test_result == cx.TestResult.PASSED
    # [END TODO TAG]
