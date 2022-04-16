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

"""Dialogflow CX webhook sample unit tests."""

import os
import uuid
import mock

import pytest
from validate_form_sample import ValidateFormSample
from contextlib import ExitStack
from webhook.main import get_webhook_uri
from common import patch_client

from google.cloud.dialogflowcx import Agent, Webhook, Intent, Page, Flow, TestCase, RunTestCaseResponse, TestCaseResult, TestResult, ConversationTurn, TestRunDifference
from sample_base import DialogflowTestCaseFailure
from google.api_core.operation import Operation


@pytest.fixture(scope="session")
def project_id():
    return os.environ["PROJECT_ID"]


@pytest.fixture(scope="session")
def build_uuid():
    return os.environ["BUILD_UUID"]


@pytest.fixture(scope="session")
def webhook_uri(project_id, build_uuid):
    return get_webhook_uri(project_id, build_uuid)


@pytest.fixture(scope="session")
def pytest_session_uuid():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def webhook_sample(project_id, webhook_uri, pytest_session_uuid):
    sample = ValidateFormSample(
        agent_display_name=f"Webhook Agent (test session {pytest_session_uuid})",
        project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.initialize()
    yield sample
    sample.tear_down()
    del sample


@pytest.mark.integration
@pytest.mark.flaky(max_runs=3, reruns_delay=15)
@pytest.mark.parametrize("test_case_display_name", ValidateFormSample.TEST_CASES)
def test_indirect(test_case_display_name, webhook_sample):
    test_case_delegator = webhook_sample.test_case_delegators[test_case_display_name]
    if test_case_delegator.expected_exception:
        with pytest.raises(test_case_delegator.expected_exception):
            test_case_delegator.run_test_case()
    else:
        test_case_delegator.run_test_case(wait=10)


@pytest.mark.hermetic
@pytest.mark.parametrize("differences,test_result,xfail", (
    ([TestRunDifference(description='XFAIL')], TestResult.FAILED, True),
    ([TestRunDifference(description='XFAIL')], TestResult.PASSED, True),
    ([], TestResult.FAILED, True),
    ([], TestResult.PASSED, False),
))
def test_basic_webhook_hermetic(differences, test_result, xfail):
    sample = ValidateFormSample(
        agent_display_name=f"MOCK_AGENT_DISPLAY_NAME",
        project_id=-1,
        webhook_uri="MOCK_WEBHOOK_URI",
    )
    sample.TEST_CASES = {
        "Test Case 0": {
            "input_text": 'MOCK_INPUT_TEXT',
            "expected_response_text": ['MOCK_EXPECTED_RESPONSE_TEXT'],
        },
    }
    with ExitStack() as stack:
        patch_client(sample.agent_delegator.client, 'create_agent', stack,
            return_value=Agent(name='MOCK_AGENT_NAME')
        )
        patch_client(sample.webhook_delegator.client, 'create_webhook', stack,
            return_value=Webhook(name='MOCK_WEBHOOK_NAME')
        )
        patch_client(sample.intent_delegator.client, 'create_intent', stack,
            return_value=Intent(name='MOCK_INTENT_NAME')
        )
        patch_client(sample.page_delegator.client, 'create_page', stack,
            return_value=Page(name='MOCK_PAGE_NAME')
        )
        patch_client(sample.start_flow_delegator.client, 'get_flow', stack,
            return_value=Flow(name='MOCK_FLOW_NAME')
        )
        patch_client(sample.page_delegator.client, 'update_page', stack)
        patch_client(sample.start_flow_delegator.client, 'update_flow', stack)
        patch_client(sample.page_delegator.client, 'delete_page', stack)
        patch_client(sample.intent_delegator.client, 'delete_intent', stack)
        patch_client(sample.webhook_delegator.client, 'delete_webhook', stack)
        patch_client(sample.agent_delegator.client, 'delete_agent', stack)
        for test_case_delegator in sample.test_case_delegators.values():
            patch_client(test_case_delegator.client, 'create_test_case', stack, return_value=
                TestCase(
                    name='MOCK_TEST_CASE_NAME',
                    display_name='MOCK_TEST_CASE_DISPLAY_NAME',
                )
            )
            patch_client(test_case_delegator.client, 'batch_delete_test_cases', stack)
            def result():
                return RunTestCaseResponse(
                    result=TestCaseResult(
                        test_result=test_result,
                        conversation_turns=[
                            ConversationTurn(
                                virtual_agent_output=ConversationTurn.VirtualAgentOutput(differences=differences)
                            )
                        ],
                    )
                )
            lro = mock.create_autospec(Operation, instance=True, spec_set=True)
            lro.result = result
            patch_client(test_case_delegator.client, 'run_test_case', stack, return_value=lro)
        sample.initialize()
        for test_case_delegator in sample.test_case_delegators.values():
            if xfail:
                with pytest.raises(DialogflowTestCaseFailure):
                    test_case_delegator.run_test_case(wait=0)
            else:
                test_case_delegator.run_test_case(wait=0)
        sample.tear_down()