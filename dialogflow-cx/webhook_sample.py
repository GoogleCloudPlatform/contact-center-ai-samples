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

_WEBHOOK_NAME = 'Webhook sample webhook'
_WEBHOOK_URI = 'Webhook sample page'
_TAG_NAME = 'webhook sample tag'
_TEST_CASE_DISPLAY_NAME = 'example_test'

_DEFAULT_AGENT_SETTINGS = {
    'agent_display_name': 'Webhook sample',
    'agent_lang_code': 'en',
    'agent_time_zone': 'America/Los_Angeles',
}


_DEFAULT_ATTRIBUTES = {
    'credentials': None,
    'location': 'global',
    'project_id': None,
}


class DialogflowController:
    '''Setup configures a Dialogflow CX agent for a webhook sample'''

    def __init__(self, **kwargs):
        '''Configures Dialogflow agent, clients and auth.'''
        self._agent = None
        self._agents_client = None
        self._webhook = None
        self._webhooks_client = None

        for key in _DEFAULT_ATTRIBUTES:
            setattr(self, key, kwargs.get(key, _DEFAULT_ATTRIBUTES[key]))

    def initialize(self):
        self.auth_default()
        self.initialize_clients()
        self.initialize_agent()

    def auth_default(self):
        self.credentials, self.project_id = google.auth.default()

    @property
    def client_options(self):
        return {"api_endpoint": f'{self.location}-dialogflow.googleapis.com'}

    @property
    def agent_parent(self):
        return f'projects/{self.project_id}/locations/{self.location}'

    @property
    def agent(self):
        if not self._agent:
            raise RuntimeError('Agent not yet created')
        return self._agent

    def create_agent(self, **_DEFAULT_AGENT_SETTINGS) -> Agent:
        '''Initializes an agent to use for the sample.'''
        self._agents_client = self._agents_client or AgentsClient(client_options=self.client_options)
        agent = Agent(**_DEFAULT_AGENT_SETTINGS)
        request = {"agent": agent, "parent": self.agent_parent}
        self._agent = self._agents_client.create_agent(request=request)

    @property
    def webhook(self):
        if not self._webhook:
            raise RuntimeError('Agent not yet created')
        return self._webhook

    def create_webhook(
            self, 
            display_name=_WEBHOOK_NAME, 
            uri=_WEBHOOK_URI,
        ):
        '''update_webhook_url updates the webhook for the webhook sample'''
        self._webhooks_client = self._webhooks_client or WebhooksClient(client_options=self.client_options)
        webhook = Webhook({
            'display_name': display_name,
            'generic_web_service': {
                'uri': uri
            }
        })
        self._webhook = self._webhooks_client.create_webhook(
            parent=self.agent.name,
            webhook=webhook
        )


    # def initialize_clients(self):
    #     self._webhooks_client = WebhooksClient(client_options=self.client_options)
    #     self._intents_client = IntentsClient(client_options=self.client_options)
    #     self._flows_client = FlowsClient(client_options=self.client_options)
    #     self._test_cases_client = TestCasesClient(client_options=self.client_options)


#     def run(self):
#         '''run sets up a Dialogflow CX agent for the webhook sample'''
#         self.webhook = self.update_webhook_url()
#         if self.args.update_agent_webhook_only:
#             return 0
#         self.setup_agent()
#         self.test_webhook(delay=5)
#         return 0

#     def test_webhook(self, delay=0):
#         '''test_webhook runs a test case to exercise the Dialogflow CX agent's webhook'''
#         # Newly created agents might need a short delay to become stable.
#         if delay:
#             time.sleep(delay)

#         # Create a test interaction, to confirm the webhook works as-intended:
#         text_response = ResponseMessage.Text(
#             text=[
#                 'Entering example_page',
#                 'Webhook received: go to example_page (Tag: webhook-tag)',
#             ]
#         )
#         virtual_agent_output = ConversationTurn.VirtualAgentOutput(
#             current_page=self.page,
#             triggered_intent=self.intent,
#             text_responses=[text_response])
#         conversation_turn = ConversationTurn(
#             virtual_agent_output=virtual_agent_output,
#             user_input=ConversationTurn.UserInput(is_webhook_enabled=True,
#             input=QueryInput(text=TextInput(text=f'go to {PAGE_NAME}'))))
#         test_case = self.clients["test_cases"].create_test_case(
#             parent=self.agent.name,
#             test_case=TestCase(display_name=TEST_CASE_DISPLAY_NAME,
#             test_case_conversation_turns=[conversation_turn],
#             test_config=TestConfig(flow=self.agent.start_flow)))
#         print(self.agent.start_flow)

#         lro = self.clients["test_cases"].run_test_case(
#             request=RunTestCaseRequest(name=test_case.name))
#         while lro.running():
#             time.sleep(1)
#         assert lro.result().result.test_result == TestResult.PASSED
#         print('Test successful!')






#     def setup_agent(self):
#         '''setup_agent creates pages, flows, and intents for the sample'''
#         # Create a page, with a webhook fulfillment:
#         fulfillment = Fulfillment({
#             'messages': [
#                 ResponseMessage(
#                     text=ResponseMessage.Text(
#                         text=[f'Entering {PAGE_NAME}']
#                     )
#                 )
#             ],
#             'webhook': self.webhook.name,
#             'tag': TAG_NAME,
#         })
#         page = Page(
#             display_name=PAGE_NAME,
#             entry_fulfillment=fulfillment,
#         )
#         self.page = self.clients["pages"].create_page(
#             parent=self.agent.start_flow,
#             page=page,
#         )

#         # Create an intent-triggered transition into the page:
#         intent = Intent({
#             'display_name':f'go-into-{PAGE_NAME}',
#             'training_phrases':[
#                 Intent.TrainingPhrase({
#                     'parts':[{
#                         'text': f'go into {PAGE_NAME}'
#                     }],
#                     'id':'',
#                     'repeat_count':1
#                 })
#             ],
#         })
#         self.intent = self.clients["intents"].create_intent(
#             parent=self.agent.name,
#             intent=intent
#         )

#         # Update start flow to transition to newly created page
#         flow = self.clients["flows"].get_flow(
#             name=self.agent.start_flow)
#         flow.transition_routes.append(TransitionRoute(
#             intent=self.intent.name,
#             target_page=self.page.name
#         ))
#         self.clients["flows"].update_flow(flow=flow)

#         print(f'New Agent: https://dialogflow.cloud.google.com/cx/{self.agent.start_flow}')


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description='Setup Dialogflow CX webhook sample')
#     parser.add_argument(
#         '--webhook-url',
#         help='Webhook URL for the Dialogflow CX to use',
#         required=True)
#     parser.add_argument(
#         '--update-agent-webhook-only',
#         help='Only update the agent\'s webhook, not NLU',
#         default=False)
#     parser.add_argument(
#         '--location',
#         help='Google Cloud location or region to create/use Dialogflow CX in',
#         default=DEFAULT_LOCATION)
#     parser.add_argument(
#         '--agent-id',
#         help='ID of the Dialogflow CX agent')
#     parser.add_argument(
#         '--agent-default-lang-code',
#         help='Default language code of the Dialogflow CX agent',
#         default=DEFAULT_AGENT_LANG_CODE)
#     parser.add_argument(
#         '--agent-display-name',
#         help='Display name of the Dialogflow CX agent',
#         default=DEFAULT_AGENT_DISPLAY_NAME)
#     parser.add_argument(
#         '--agent-time-zone',
#         help='Time zone of the Dialogflow CX agent',
#         default=DEFAULT_AGENT_TIME_ZONE)
#     parser.add_argument(
#         '--project-id',
#         help='Google Cloud project to create/use Dialogflow CX in')
#     main = Setup(args=parser.parse_args())
#     sys.exit(main.run())
