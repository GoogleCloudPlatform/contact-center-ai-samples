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

"""Dialogflow TestCase API interactions."""

import time

import dialogflow_sample as ds
import google.api_core.exceptions
import google.auth
import google.cloud.dialogflowcx as cx

from .client_delegator import ClientDelegator


class DialogflowTestCaseFailure(Exception):
    """Exception to raise when a test case fails"""


class TestCaseDelegator(ClientDelegator):
    """Class for organizing interactions with the Dialogflow TestCases API."""

    _CLIENT_CLASS = cx.TestCasesClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        self._is_webhook_enabled = kwargs.pop("is_webhook_enabled", False)
        self._conversation_turns = kwargs.pop("conversation_turns")
        self.expected_exception = kwargs.pop("expected_exception", None)
        self._test_case = None
        super().__init__(controller, **kwargs)

    @property
    def test_case(self):
        """Test Case set in Dialogflow."""
        if not self._test_case:
            raise RuntimeError("Test Case not yet created")
        return self._test_case

    def setup(self):
        """Initializes the test cases delegator."""
        try:
            self._test_case = self.client.create_test_case(
                parent=self.controller.agent_delegator.agent.name,
                test_case=cx.TestCase(
                    display_name=self.display_name,
                    test_case_conversation_turns=[
                        t.get_conversation_turn(self._is_webhook_enabled)
                        for t in self._conversation_turns
                    ],
                    test_config=cx.TestConfig(flow=self.controller.start_flow),
                ),
            )
        except google.api_core.exceptions.AlreadyExists:
            request = cx.ListTestCasesRequest(parent=self.parent)
            for curr_test_case in self.client.list_test_cases(request=request):
                if curr_test_case.display_name == self.display_name:
                    request = cx.GetTestCaseRequest(
                        name=curr_test_case.name,
                    )
                    self._test_case = self.client.get_test_case(request=request)
                    return

    def tear_down(self):
        """Destroys the test case."""
        request = cx.BatchDeleteTestCasesRequest(
            parent=self.parent,
            names=[self.test_case.name],
        )
        try:
            self.client.batch_delete_test_cases(request=request)
            self._test_case = None
        except google.api_core.exceptions.NotFound:
            pass

    def run_test_case(self, wait=10, max_retries=3):
        """Runs the test case."""
        retry_count = 0
        result = None
        while retry_count < max_retries:
            time.sleep(wait)
            lro = self.client.run_test_case(
                request=cx.RunTestCaseRequest(name=self.test_case.name)
            )
            while lro.running():
                try:
                    result = lro.result().result
                    agent_response_differences = [
                        conversation_turn.virtual_agent_output.differences
                        for conversation_turn in result.conversation_turns
                    ]
                    test_case_fail = result.test_result != cx.TestResult.PASSED
                    if any(agent_response_differences) or test_case_fail:
                        raise DialogflowTestCaseFailure(
                            f'Test "{self.test_case.display_name}" failed'
                        )
                    return
                except google.api_core.exceptions.NotFound as exc:
                    if str(exc) == (
                        "404 com.google.apps.framework.request.NotFoundException: "
                        "NLU model for flow '00000000-0000-0000-0000-000000000000' does not exist. "
                        "Please try again after retraining the flow."
                    ):
                        retry_count += 1
        raise RuntimeError(f"Retry count exceeded: {retry_count}")
