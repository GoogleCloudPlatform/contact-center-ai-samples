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

"""setup.py calls the DIalogflow API to setup a webhook sample"""

import argparse
import time
import sys

import google.auth
from google.cloud.dialogflowcx_v3 import (
    Agent,
    AgentsClient,
    FlowsClient,
    Fulfillment,
    Intent,
    IntentsClient,
    Page,
    PagesClient,
    ResponseMessage,
    TransitionRoute,
    Webhook,
    WebhooksClient,
    ConversationTurn,
    TestCase,
    TestCasesClient,
    TestConfig,
    RunTestCaseRequest,
    TestResult,
    QueryInput,
    TextInput,
)

DEFAULT_LOCATION = "global"
DEFAULT_AGENT_LANG_CODE = "en"
DEFAULT_AGENT_DISPLAY_NAME = "Webhook sample"
TEST_CASE_DISPLAY_NAME = "example_test"
DEFAULT_AGENT_TIME_ZONE = "America/Los_Angeles"
WEBHOOK_NAME = "Webhook sample webhook"
PAGE_NAME = "Webhook sample page"
TAG_NAME = "webhook sample tag"


class Setup:
    """Setup configures a Dialogflow CX agent for a webhook sample"""

    def __init__(self, args):
        """__init__ gets Dialogflow agent, clients and auth"""
        if not args.project_id:
            _, project_id = google.auth.default()
            args.project_id = project_id
        self.project_id = args.project_id
        self.args = args

        client_options = {
            "api_endpoint": f"{self.args.location}-dialogflow.googleapis.com"
        }
        self.clients = {
            "agents": AgentsClient(client_options=client_options),
            "pages": PagesClient(client_options=client_options),
            "webhooks": WebhooksClient(client_options=client_options),
            "intents": IntentsClient(client_options=client_options),
            "flows": FlowsClient(client_options=client_options),
            "test_cases": TestCasesClient(client_options=client_options),
        }
        # Create or get Dialogflow CX agent.
        if not self.args.agent_id:
            self.agent = self.create_agent()
        else:
            self.agent = self.get_agent()

        self.webhook = None
        self.intent = None
        self.page = None

    def run(self):
        """run sets up a Dialogflow CX agent for the webhook sample"""
        self.webhook = self.update_webhook_url()
        if self.args.update_agent_webhook_only:
            return 0
        self.setup_agent()
        self.test_webhook(delay=5)
        return 0

    def test_webhook(self, delay=0):
        """test_webhook runs a test case to exercise the Dialogflow CX agent's webhook"""
        # Newly created agents might need a short delay to become stable.
        if delay:
            time.sleep(delay)

        # Create a test interaction, to confirm the webhook works as-intended:
        text_response = ResponseMessage.Text(
            text=[
                "Entering example_page",
                "Webhook received: go to example_page (Tag: webhook-tag)",
            ]
        )
        virtual_agent_output = ConversationTurn.VirtualAgentOutput(
            current_page=self.page,
            triggered_intent=self.intent,
            text_responses=[text_response],
        )
        conversation_turn = ConversationTurn(
            virtual_agent_output=virtual_agent_output,
            user_input=ConversationTurn.UserInput(
                is_webhook_enabled=True,
                input=QueryInput(text=TextInput(text=f"go to {PAGE_NAME}")),
            ),
        )
        test_case = self.clients["test_cases"].create_test_case(
            parent=self.agent.name,
            test_case=TestCase(
                display_name=TEST_CASE_DISPLAY_NAME,
                test_case_conversation_turns=[conversation_turn],
                test_config=TestConfig(flow=self.agent.start_flow),
            ),
        )
        print(self.agent.start_flow)

        lro = self.clients["test_cases"].run_test_case(
            request=RunTestCaseRequest(name=test_case.name)
        )
        while lro.running():
            time.sleep(1)
        assert lro.result().result.test_result == TestResult.PASSED
        print("Test successful!")

    def create_agent(self):
        """create_agent creates a agent for the webhook sample"""
        parent = f"projects/{self.project_id}/locations/{self.args.location}"
        agent = Agent(
            display_name=self.args.agent_display_name,
            default_language_code=self.args.agent_default_lang_code,
            time_zone=self.args.agent_time_zone,
        )
        request = {"agent": agent, "parent": parent}
        return self.clients["agents"].create_agent(request=request)

    def get_agent(self):
        """get_agent gets an existing agent to use for the webhook sample"""
        parent = f"projects/{self.project_id}/locations/{self.args.location}"
        return self.clients["agents"].get_agent(request={"parent": parent})

    def update_webhook_url(self):
        """update_webhook_url updates the webhook for the webhook sample"""
        webhook = Webhook(
            {
                "display_name": WEBHOOK_NAME,
                "generic_web_service": {"uri": self.args.webhook_url},
            }
        )
        return self.clients["webhooks"].create_webhook(
            parent=self.agent.name, webhook=webhook
        )

    def setup_agent(self):
        """setup_agent creates pages, flows, and intents for the sample"""
        # Create a page, with a webhook fulfillment:
        fulfillment = Fulfillment(
            {
                "messages": [
                    ResponseMessage(
                        text=ResponseMessage.Text(text=[f"Entering {PAGE_NAME}"])
                    )
                ],
                "webhook": self.webhook.name,
                "tag": TAG_NAME,
            }
        )
        page = Page(
            display_name=PAGE_NAME,
            entry_fulfillment=fulfillment,
        )
        self.page = self.clients["pages"].create_page(
            parent=self.agent.start_flow,
            page=page,
        )

        # Create an intent-triggered transition into the page:
        intent = Intent(
            {
                "display_name": f"go-into-{PAGE_NAME}",
                "training_phrases": [
                    Intent.TrainingPhrase(
                        {
                            "parts": [{"text": f"go into {PAGE_NAME}"}],
                            "id": "",
                            "repeat_count": 1,
                        }
                    )
                ],
            }
        )
        self.intent = self.clients["intents"].create_intent(
            parent=self.agent.name, intent=intent
        )

        # Update start flow to transition to newly created page
        flow = self.clients["flows"].get_flow(name=self.agent.start_flow)
        flow.transition_routes.append(
            TransitionRoute(intent=self.intent.name, target_page=self.page.name)
        )
        self.clients["flows"].update_flow(flow=flow)

        print(
            f"New Agent: https://dialogflow.cloud.google.com/cx/{self.agent.start_flow}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup Dialogflow CX webhook sample")
    parser.add_argument(
        "--webhook-url", help="Webhook URL for the Dialogflow CX to use", required=True
    )
    parser.add_argument(
        "--update-agent-webhook-only",
        help="Only update the agent's webhook, not NLU",
        default=False,
    )
    parser.add_argument(
        "--location",
        help="Google Cloud location or region to create/use Dialogflow CX in",
        default=DEFAULT_LOCATION,
    )
    parser.add_argument("--agent-id", help="ID of the Dialogflow CX agent")
    parser.add_argument(
        "--agent-default-lang-code",
        help="Default language code of the Dialogflow CX agent",
        default=DEFAULT_AGENT_LANG_CODE,
    )
    parser.add_argument(
        "--agent-display-name",
        help="Display name of the Dialogflow CX agent",
        default=DEFAULT_AGENT_DISPLAY_NAME,
    )
    parser.add_argument(
        "--agent-time-zone",
        help="Time zone of the Dialogflow CX agent",
        default=DEFAULT_AGENT_TIME_ZONE,
    )
    parser.add_argument(
        "--project-id", help="Google Cloud project to create/use Dialogflow CX in"
    )
    main = Setup(args=parser.parse_args())
    sys.exit(main.run())
