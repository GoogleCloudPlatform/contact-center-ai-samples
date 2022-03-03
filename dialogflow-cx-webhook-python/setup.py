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

import sys
import argparse

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
)

DEFAULT_LOCATION = 'us-central1'
DEFAULT_AGENT_LANG_CODE = 'en'
DEFAULT_AGENT_DISPLAY_NAME = 'Webhook sample'
DEFAULT_AGENT_TIME_ZONE = 'America/Los_Angeles'
WEBHOOK_NAME = 'Webhook sample webhook'
PAGE_NAME = 'Webhook sample page'
TAG_NAME = 'webhook sample tag'

class Setup:
    '''Setup configures a Dialogflow CX agent for a webhook sample'''
    def __init__(self, args):
        '''__init__ gets Dialogflow agent, clients and auth'''
        _, project_id = google.auth.default()
        self.project_id = project_id
        self.args = args

        client_options = {
            "api_endpoint": f'{self.args.location}-dialogflow.googleapis.com'
        }
        self.agents_client = AgentsClient(client_options=client_options)
        self.pages_client = PagesClient(client_options=client_options)
        self.webhooks_client = WebhooksClient(client_options=client_options)
        self.intents_client = IntentsClient(client_options=client_options)
        self.flows_client = FlowsClient(client_options=client_options)

        # Create or get Dialogflow CX agent.
        if not self.args.agent_id:
            self.agent = self.create_agent()
        else:
            self.agent = self.get_agent()

        self.webhook = None


    def run(self):
        '''run sets up a Dialogflow CX agent for the webhook sample'''
        self.webhook = self.update_webhook_url()
        if self.args.update_agent_webhook_only:
            return 0
        self.setup_agent()

    def create_agent(self):
        '''create_agent creates a agent for the webhook sample'''
        parent = f'projects/{self.project_id}/locations/{self.args.location}'
        agent = Agent(
            display_name=self.args.agent_display_name,
            default_language_code=self.args.agent_default_lang_code,
            time_zone=self.args.agent_time_zone,
        )
        request = {"agent": agent, "parent": parent}
        return self.agents_client.create_agent(request=request)

    def get_agent(self):
        '''get_agent gets an existing agent to use for the webhook sample'''
        parent = f'projects/{self.project_id}/locations/{self.args.location}'
        return self.agents_client.get_agent(request={"parent": parent})

    def update_webhook_url(self):
        '''update_webhook_url updates the webhook for the webhook sample'''
        webhook = Webhook({
            'display_name': WEBHOOK_NAME,
            'generic_web_service': {
                'uri': self.args.webhook_url
            }
        })
        return self.webhooks_client.create_webhook(
            parent=self.agent.name,
            webhook=webhook
        )

    def setup_agent(self):
        '''setup_agent creates pages, flows, and intents for the sample'''
        # Create a page, with a webhook filfillment:
        fulfillment = Fulfillment({
            'messages': [
                ResponseMessage(
                    text=ResponseMessage.Text(
                        text=[f'Entering {PAGE_NAME}']
                    )
                )
            ],
            'webhook': self.webhook.name,
            'tag': TAG_NAME,
        })
        page = Page(
            display_name=PAGE_NAME,
            entry_fulfillment=fulfillment,
        )
        page = self.pages_client.create_page(
            parent=self.agent.start_flow.name,
            page=page,
        )

        # Create an intent-triggered transition into the page:
        intent = Intent({
            'display_name':f'go-into-{PAGE_NAME}',
            'training_phrases':[
                Intent.TrainingPhrase({
                    'parts':[{
                        'text': f'go into {PAGE_NAME}'
                    }],
                    'id':'',
                    'repeat_count':1
                })
            ],
        })
        intent = self.intents_client.create_intent(
            parent=self.agent.name,
            intent=intent
        )

        # Update start flow to transition to newly created page
        flow = self.flows_client.get_flow(
            name=self.agent.start_flow)
        flow.transition_routes.append(TransitionRoute(
            intent=intent.name,
            target_page=page.name
        ))
        self.flows_client.update_flow(flow=flow)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Setup Dialogflow CX webhook sample')
    parser.add_argument(
        '--webhook-url',
        help='Webhook URL for the Dialogflow CX to use',
        required=True)
    parser.add_argument(
        '--update-agent-webhook-only',
        help='Only update the agent\'s webhook, not NLU',
        default=False)
    parser.add_argument(
        '--location',
        help='Google Cloud location or region to create/use Dialogflow CX in',
        default=DEFAULT_LOCATION)
    parser.add_argument(
        '--agent-id',
        help='ID of the Dialogflow CX agent')
    parser.add_argument(
        '--agent-default-lang-code',
        help='Default language code of the Dialogflow CX agent',
        default=DEFAULT_AGENT_LANG_CODE)
    parser.add_argument(
        '--agent-display-name',
        help='Display name of the Dialogflow CX agent',
        default=DEFAULT_AGENT_DISPLAY_NAME)
    parser.add_argument(
        '--agent-time-zone',
        help='Time zone of the Dialogflow CX agent',
        default=DEFAULT_AGENT_TIME_ZONE)
    main = Setup(args=parser.parse_args())
    sys.exit(main.run())
