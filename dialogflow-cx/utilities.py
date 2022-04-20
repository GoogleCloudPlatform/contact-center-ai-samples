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

"""Helper functions for creating and testing Dialogflow CX samples."""

import contextlib
import time
from contextlib import ExitStack
from dataclasses import dataclass, field
from typing import Mapping

import google.api_core.exceptions
import google.cloud.dialogflowcx as cx
import mock
from google.api_core.operation import Operation


@dataclass
class RequestMock:
    """Mocks a flask.Request interface for testing webhooks."""

    payload: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def get_json(self) -> Mapping:
        """Method for returning the payload via the get_json interface."""
        return self.payload


def patch_client(client, method_name, stack, return_value=None):
    """Patches the Dialogflow CX client object for hermetic testing."""
    stack.enter_context(
        mock.patch.object(
            client,
            method_name,
            return_value=return_value,
        )
    )


hermetic_test_cases = [
    ([cx.TestRunDifference(description="XFAIL")], cx.TestResult.FAILED, True),
    ([cx.TestRunDifference(description="XFAIL")], cx.TestResult.PASSED, True),
    ([], cx.TestResult.FAILED, True),
    ([], cx.TestResult.PASSED, False),
]


def run_hermetic_test(sample):
    """Drives a hermetic sample test suite by mocking out client interactions."""
    user_input = ["MOCK_USER_INPUT"]
    with ExitStack() as stack:
        patch_client(
            sample.agent_delegator.client,
            "create_agent",
            stack,
            return_value=cx.Agent(name="MOCK_AGENT_NAME"),
        )
        patch_client(
            sample.webhook_delegator.client,
            "create_webhook",
            stack,
            return_value=cx.Webhook(name="MOCK_WEBHOOK_NAME"),
        )
        patch_client(
            sample.intent_delegator.client,
            "create_intent",
            stack,
            return_value=cx.Intent(name="MOCK_INTENT_NAME"),
        )
        patch_client(
            sample.page_delegator.client,
            "create_page",
            stack,
            return_value=cx.Page(name="MOCK_PAGE_NAME"),
        )
        patch_client(
            sample.start_flow_delegator.client,
            "get_flow",
            stack,
            return_value=cx.Flow(name="MOCK_FLOW_NAME"),
        )
        patch_client(sample.page_delegator.client, "update_page", stack)
        patch_client(sample.start_flow_delegator.client, "update_flow", stack)
        lro = mock.create_autospec(Operation, instance=True, spec_set=True)
        lro.running = lambda: False
        patch_client(
            sample.start_flow_delegator.client, "train_flow", stack, return_value=lro
        )
        patch_client(sample.page_delegator.client, "delete_page", stack)
        patch_client(sample.intent_delegator.client, "delete_intent", stack)
        patch_client(sample.webhook_delegator.client, "delete_webhook", stack)
        patch_client(sample.agent_delegator.client, "delete_agent", stack)
        patch_client(
            sample.test_cases_client,
            "create_test_case",
            stack,
            return_value=cx.TestCase(
                name="MOCK_TEST_CASE_NAME",
                display_name="MOCK_TEST_CASE_DISPLAY_NAME",
            ),
        )
        patch_client(sample.test_cases_client, "batch_delete_test_cases", stack)
        patch_client(
            sample.session_delegator.client,
            "detect_intent",
            stack,
            return_value=cx.DetectIntentResponse(),
        )

        def result():
            return cx.RunTestCaseResponse(
                result=cx.TestCaseResult(
                    test_result=cx.TestResult.PASSED,
                    conversation_turns=[
                        cx.ConversationTurn(
                            virtual_agent_output=cx.ConversationTurn.VirtualAgentOutput(
                                differences=[],
                            )
                        )
                    ],
                )
            )

        lro = mock.create_autospec(Operation, instance=True, spec_set=True)
        lro.result = result
        patch_client(sample.test_cases_client, "run_test_case", stack, return_value=lro)
        sample.setup()
        sample.run(user_input, quiet=True)
        sample.tear_down()


@contextlib.contextmanager
def retry_call(api_method, request, max_retries=3, delay=1):
    """Retry an api call multiple times if needed."""
    retry_count = 0
    result = None
    while retry_count < max_retries:
        try:
            result = api_method(request)
            break
        except google.api_core.exceptions.NotFound as exc:
            if str(exc) == (
                "404 com.google.apps.framework.request.NotFoundException: "
                "NLU model for flow '00000000-0000-0000-0000-000000000000' does not exist. "
                "Please try again after retraining the flow."
            ):
                retry_count += 1
                time.sleep(delay)

    if retry_count == max_retries:
        raise RuntimeError("Too many return attempts")

    yield result


def create_conversational_turn(
    user_input, agent_response_list, triggered_intent, output_page, is_webhook_enabled
):
    """Create a conversational turn."""
    turn = cx.ConversationTurn(
        virtual_agent_output=cx.ConversationTurn.VirtualAgentOutput(
            current_page=output_page,
            triggered_intent=triggered_intent,
            text_responses=[
                cx.ResponseMessage.Text(text=text) for text in agent_response_list
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

    return turn
