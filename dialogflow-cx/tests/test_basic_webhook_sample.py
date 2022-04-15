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
from contextlib import ExitStack

from google.cloud.dialogflowcx import Agent, Webhook, Intent, Page, Flow, TestCase

import pytest
from basic_webhook_sample import BasicWebhookSample
from webhook.main import get_webhook_uri


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
    sample = BasicWebhookSample(
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
@pytest.mark.parametrize("test_case_display_name", BasicWebhookSample.TEST_CASES)
def test_basic_webhook_integration(test_case_display_name, webhook_sample):
    test_case_delegator = webhook_sample.test_case_delegators[test_case_display_name]
    if test_case_delegator.expected_exception:
        with pytest.raises(test_case_delegator.expected_exception):
            test_case_delegator.run_test_case()
    else:
        test_case_delegator.run_test_case(wait=10)

from google.api_core.operation import Operation

@pytest.mark.hermetic
def test_basic_webhook_hermetic():
    sample = BasicWebhookSample(
        agent_display_name=f"MOCK_AGENT_DISPLAY_NAME",
        project_id=-1,
        webhook_uri="MOCK_WEBHOOK_URI",
    )
    with ExitStack() as stack:
        create_agent_mock = stack.enter_context(
            mock.patch.object(
                sample.agent_delegator.client, 
                'create_agent', 
                return_value=Agent(name='MOCK_AGENT_NAME')
            )
        )
        create_webhook_mock = stack.enter_context(
            mock.patch.object(
                sample.webhook_delegator.client, 
                'create_webhook', 
                return_value=Webhook(name='MOCK_WEBHOOK_NAME')
            )
        )
        create_intent_mock = stack.enter_context(
            mock.patch.object(
                sample.intent_delegator.client, 
                'create_intent', 
                return_value=Intent(name='MOCK_INTENT_NAME')
            )
        )
        create_page_mock = stack.enter_context(
            mock.patch.object(
                sample.page_delegator.client, 
                'create_page', 
                return_value=Page(name='MOCK_PAGE_NAME')
            )
        )
        get_flow_mock = stack.enter_context(
            mock.patch.object(
                sample.start_flow_delegator.client, 
                'get_flow', 
                return_value=Flow(name='MOCK_FLOW_NAME')
            )
        )
        update_flow_mock = stack.enter_context(
            mock.patch.object(
                sample.start_flow_delegator.client, 
                'update_flow'
            )
        )
        for test_case_delegator in sample.test_case_delegators.values():
            stack.enter_context(
                mock.patch.object(
                    test_case_delegator.client, 
                    'create_test_case', 
                    return_value=TestCase(
                        name='MOCK_TEST_CASE_NAME', 
                        display_name='MOCK_TEST_CASE_DISPLAY_NAME',
                    ),
                )
            )
            stack.enter_context(
                mock.patch.object(
                    test_case_delegator.client, 
                    'run_test_case', 
                    return_value=mock.create_autospec(Operation, instance=True, spec_set=True)
                )
            )

        sample.initialize()
        for test_case_delegator in sample.test_case_delegators.values():
            if test_case_delegator.expected_exception:
                continue
            else:
                test_case_delegator.run_test_case(wait=0)
                # pass


    # sample.agent_delegator.client.transport.create_agent = mock.patch()
    # with mock.patch.object(type(sample.agent_delegator.client.transport.create_agent), "__call__") as call:
        # with mock.patch.object(type(sample.webhook_delegator.client.transport.create_webhook), "__call__") as call_a:
        # with mock.patch.object(_UnaryUnaryMultiCallable, "__call__") as call: