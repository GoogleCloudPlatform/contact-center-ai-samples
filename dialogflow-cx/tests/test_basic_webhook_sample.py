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

import uuid

from google.cloud.dialogflowcx_v3.types import agent as gcdc_agent
from google.cloud.dialogflowcx_v3 import Agent
import google.auth
import pytest
import os
from google.cloud.dialogflowcx_v3.services.agents import AgentsClient
from google.auth import credentials as ga_credentials
from grpc._channel import _UnaryUnaryMultiCallable

from basic_webhook_sample import BasicWebhookSample
from webhook.main import get_webhook_uri


@pytest.fixture(scope='session')
def project_id():
  return os.environ["PROJECT_ID"]


@pytest.fixture(scope='session')
def build_uuid():
  return os.environ["BUILD_UUID"]


@pytest.fixture(scope='session')
def webhook_uri(project_id, build_uuid):
  return get_webhook_uri(project_id, build_uuid)


@pytest.fixture(scope='session')
def pytest_session_uuid():
  return uuid.uuid4()


@pytest.fixture(scope='session')
def webhook_sample(project_id, webhook_uri, pytest_session_uuid):
  sample = BasicWebhookSample(
    agent_display_name = f'Webhook Agent (test session {pytest_session_uuid})',
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
def test_indirect(test_case_display_name, webhook_sample):
  test_case_delegator = webhook_sample.test_case_delegators[test_case_display_name]
  if test_case_delegator.expected_exception:
    with pytest.raises(test_case_delegator.expected_exception) as e_info:
      test_case_delegator.run_test_case()
  else:
    test_case_delegator.run_test_case(wait=10)