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

"""Dialogflow CX webhook sample unit tests"""

import argparse
import unittest
from unittest.mock import MagicMock, patch

from main import Setup

WEBHOOK_URL = "webhook_url"
LOCATION = "location"
AGENT_ID = "agent_id"
AGENT_DEFAULT_LANG_CODE = "agent_default_lang_code"
AGENT_DISPLAY_NAME = "agent_display_name"
AGENT_TIME_ZONE = "agent_time_zone"
PROJECT_ID = "project_id"


class TestSetup(unittest.TestCase):
    """Test class for Dialogflow CX webhook sample"""

    @patch("main.AgentsClient")
    @patch("main.PagesClient")
    @patch("main.WebhooksClient")
    @patch("main.IntentsClient")
    @patch("main.FlowsClient")
    @patch("main.TestCasesClient")
    # pylint: disable=too-many-arguments,no-self-use
    def test_init(
        self,
        mock_agents_client,
        mock_pages_client,
        mock_webhooks_client,
        mock_intents_client,
        mock_flows_client,
        mock_test_cases_client,
    ):
        """Test for the Setup class' init method"""

        # Mock all Dialogflow clients to prevent clients for searching for ADC
        # in the local environment and throwing errors.
        mock_agents_client.return_value = MagicMock()
        mock_pages_client.return_value = MagicMock()
        mock_webhooks_client.return_value = MagicMock()
        mock_intents_client.return_value = MagicMock()
        mock_flows_client.return_value = MagicMock()
        mock_test_cases_client.return_value = MagicMock()

        test_args = argparse.Namespace(
            webhook_url=WEBHOOK_URL,
            update_agent_webhook_only=False,
            location=LOCATION,
            agent_id=AGENT_ID,
            agent_default_lang_code=AGENT_DEFAULT_LANG_CODE,
            agent_display_name=AGENT_DISPLAY_NAME,
            agent_time_zone=AGENT_TIME_ZONE,
            project_id=PROJECT_ID,
        )

        setup = Setup(test_args)

        assert setup.args == test_args
        assert setup.project_id == PROJECT_ID


if __name__ == "__main__":
    unittest.main()
