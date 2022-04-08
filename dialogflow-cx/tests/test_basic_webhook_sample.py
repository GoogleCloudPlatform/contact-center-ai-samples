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

from basic_webhook_sample import WebhookSample
from basic_webhook import main as basic_webhook_main

'''
export TERRAFORM_PROJECT_ID=df-terraform-dev-1113
'''


@pytest.fixture(scope='function')
def project_id():
  return os.environ["TERRAFORM_PROJECT_ID"]


@pytest.fixture(scope='function')
def webhook_uri(project_id):
  webhook_name = basic_webhook_main.basic_dialogflow_webhook.__name__

  return f'https://us-central1-{project_id}.cloudfunctions.net/{webhook_name}'


@pytest.fixture(scope='session')
def pytest_session_uuid():
  return uuid.uuid4()


@pytest.fixture(scope='function')
def webhook_sample(project_id, webhook_uri, pytest_session_uuid):
  sample = WebhookSample(
    agent_display_name = f'Webhook Agent (test session {pytest_session_uuid})',
    project_id=project_id,
    webhook_uri=webhook_uri,
  )
  sample.initialize()
  yield sample
  del sample


@pytest.mark.integration
@pytest.mark.flaky(max_runs=3, reruns_delay=15)
@pytest.mark.parametrize("test_case_display_name", WebhookSample.TEST_CASES)
def test_indirect(test_case_display_name, webhook_sample):
  test_case_delegator = webhook_sample.test_case_delegators[test_case_display_name]
  if test_case_delegator.expected_exception:
    with pytest.raises(test_case_delegator.expected_exception) as e_info:
      test_case_delegator.run_test_case()
  else:
    test_case_delegator.run_test_case(wait=10)







  #, WebhookSample.TESTS)
    # assert len(fixt) == 3

    # sample = WebhookSample(quota_project_id='df-terraform-dev04cc')
    # sample.initialize()
    # for test_case_delegator in sample.test_case_delegators:
    #     test_case_delegator.run_test_case()

# from webhook_sample import DialogflowController, _DEFAULT_ATTRIBUTES


# def test_dialogflow_controller_init_default():
#     """Test for the Setup class' init method"""
#     # Act:
#     dfc = DialogflowController()
    
#     # Assert:
#     for key, val in _DEFAULT_ATTRIBUTES.items():
#       assert getattr(dfc, key) == val


# def test_dialogflow_controller_init_override_project_id(project_id):
#     """Test for the Setup class' init method"""
#     # Act:
#     dfc = DialogflowController(project_id=project_id)
    
#     # Assert:
#     dfc.project_id == project_id


# def test_dialogflow_controller_auth_default(controller, mock_project_id_env, mocker, mock_credentials):
#   # Arrange:
#   assert controller.credentials!=mock_project_id_env
#   assert controller.project_id!=mock_project_id_env
#   mocker.patch('google.auth.default', return_value=(mock_credentials, google.auth.default()[1]) )

#   # Act:
#   controller.auth_default()

#   # Assert:
#   assert controller.project_id==mock_project_id_env
#   assert controller.credentials==mock_credentials


# def test_dialogflow_controller_create_agent(controller):
#   # Act:
#   with mock.patch.object(_UnaryUnaryMultiCallable, "__call__") as call:
#       controller.create_agent()

#   # Assert:
#   assert len(call.mock_calls) == 1
#   _, args, _ = call.mock_calls[0]
#   assert args[0].parent == controller.agent_parent


# def test_dialogflow_controller_create_webhook(controller):
#   # Arrange:
#   controller._agent = Agent(name='MOCK_AGENT_NAME')
#   # .name = 

#   # Act:
#   with mock.patch.object(_UnaryUnaryMultiCallable, "__call__") as call:
#       controller.create_webhook()

#   # Assert:
#   assert len(call.mock_calls) == 1
#   _, args, _ = call.mock_calls[0]
#   assert args[0].parent == controller.agent.name



# class TestSetup(unittest.TestCase):
#     """Test class for Dialogflow CX webhook sample"""

#     @patch("main.AgentsClient")
#     @patch("main.PagesClient")
#     @patch("main.WebhooksClient")
#     @patch("main.IntentsClient")
#     @patch("main.FlowsClient")
#     @patch("main.TestCasesClient")

# self,
#     mock_agents_client,
#     mock_pages_client,
#     mock_webhooks_client,
#     mock_intents_client,
#     mock_flows_client,
#     mock_test_cases_client

    # Mock all Dialogflow clients to prevent clients for searching for ADC
    # in the local environment and throwing errors.
    # mock_agents_client.return_value = MagicMock()
    # mock_pages_client.return_value = MagicMock()
    # mock_webhooks_client.return_value = MagicMock()
    # mock_intents_client.return_value = MagicMock()
    # mock_flows_client.return_value = MagicMock()
    # mock_test_cases_client.return_value = MagicMock()

    # test_args = argparse.Namespace(
    #     webhook_url=WEBHOOK_URL,
    #     update_agent_webhook_only=False,
    #     location=LOCATION,
    #     agent_id=AGENT_ID,
    #     agent_default_lang_code=AGENT_DEFAULT_LANG_CODE,
    #     agent_display_name=AGENT_DISPLAY_NAME,
    #     agent_time_zone=AGENT_TIME_ZONE,
    #     project_id=PROJECT_ID,
    # )

    # setup = Setup(test_args)

    # assert setup.args == test_args
    # assert setup.project_id == PROJECT_ID
