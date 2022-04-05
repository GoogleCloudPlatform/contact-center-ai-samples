from google.cloud.dialogflowcx import AgentsClient, Agent, ListAgentsRequest, GetAgentRequest
from google.cloud.dialogflowcx import Webhook, WebhooksClient, ListWebhooksRequest, GetWebhookRequest
from google.cloud.dialogflowcx import Intent, IntentsClient, ListIntentsRequest, GetIntentRequest
from google.cloud.dialogflowcx import Page, PagesClient, ListPagesRequest, GetPageRequest

import google.auth
import google.api_core.exceptions


class DialogflowSample:
    """Base class for samples"""

    @property
    def project_id(self):
        return self.auth_delegator.project_id

    @property
    def location(self):
        return self.auth_delegator.location

    @property
    def start_flow(self):
        return self.agent_delegator.start_flow


class ClientDelegator:

    _CLIENT_CLASS = None  # Override in subclass

    def __init__(self, controller: DialogflowSample, client=None):
        self.controller = controller
        self._client = client

    @property
    def client_options(self):
        return {"api_endpoint": f'{self.controller.location}-dialogflow.googleapis.com'}

    @property
    def client(self):
      if self._client is None: 
        self._client = self._CLIENT_CLASS(client_options=self.client_options)
      return self._client

    @property
    def parent(self):
        return self.controller.agent_delegator.agent.name


class AgentDelegator(ClientDelegator):

    _DEFAULT_LANGUAGE_CODE = 'en'
    _DEFAULT_TIME_ZONE = 'America/Los_Angeles'
    _CLIENT_CLASS = AgentsClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
      super().__init__(controller)
      self._display_name = kwargs['display_name']
      self.default_language_code = kwargs.get('default_language_code', self._DEFAULT_LANGUAGE_CODE)
      self.time_zone = kwargs.get('time_zone', self._DEFAULT_TIME_ZONE)

    def initialize(self):
        '''Initializes an agent to use for the sample.'''
        try:
          agent = Agent(
              display_name=self._display_name,
              default_language_code=self.default_language_code,
              time_zone=self.time_zone,
          )
          request = {"agent": agent, "parent": self.parent}
          self._agent = self.client.create_agent(request=request)
        except google.api_core.exceptions.AlreadyExists:
          request = ListAgentsRequest(
            parent=self.parent,
          )
          for agent in self.client.list_agents(request=request):
            if agent.display_name == self._display_name:
              request = GetAgentRequest(
                  name=agent.name,
              )
              self._agent = self.client.get_agent(request=request)
              break

    @property
    def parent(self):
        return f'projects/{self.controller.project_id}/locations/{self.controller.location}'

    @property
    def agent(self):
        if not self._agent:
            raise RuntimeError('Agent not yet created')
        return self._agent

    @property
    def start_flow(self):
      return self.agent.start_flow


class AuthDelegator:

    _DEFAULT_LOCATION = 'global'

    def __init__(self, controller: DialogflowSample, quota_project_id=None, **kwargs):
        self.controller = controller
        self.credentials, self.project_id = google.auth.default(quota_project_id=quota_project_id)
        self.location = kwargs.get('location', self._DEFAULT_LOCATION)


class WebhookDelegator(ClientDelegator):

    _CLIENT_CLASS = WebhooksClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller)
        self._display_name = kwargs['display_name']
        self._uri = kwargs['uri']


    @property
    def webhook(self):
        if not self._webhook:
            raise RuntimeError('Webhook not yet created')
        return self._webhook

    def initialize(self):
        '''Initializes an agent to use for the sample.'''
        webhook = Webhook({
            'display_name': self._display_name,
            'generic_web_service': {
                'uri': self._uri
            }
        })
        try:
          self._webhook = self.client.create_webhook(
              parent=self.parent,
              webhook=webhook,
          )
        except google.api_core.exceptions.AlreadyExists:
          request = ListWebhooksRequest(
            parent=self.parent,
          )
          for webhook in self.client.list_webhooks(request=request):
            if webhook.display_name == self._display_name:
              request = GetWebhookRequest(
                  name=webhook.name,
              )
              self._webhook = self.client.get_webhook(request=request)
              break


class IntentDelegator(ClientDelegator):

    _CLIENT_CLASS = IntentsClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller)
        self._display_name = kwargs['display_name']

    @property
    def intent(self):
        if not self._intent:
            raise RuntimeError('Intent not yet created')
        return self._intent

    def initialize(self, training_phrases_text):
        # Create an intent-triggered transition into the page:

        try:
          training_phrases = []
          for training_phrase_text in training_phrases_text:
            training_phrase = Intent.TrainingPhrase({
                'parts':[{
                    'text': f'{training_phrase_text}'
                }],
                'id':'',
                'repeat_count':1
            })
            training_phrases.append(training_phrase)

          intent = Intent({
              'display_name':self._display_name,
              'training_phrases':training_phrases,
          })

          self._intent = self.client.create_intent(
              parent=self.parent,
              intent=intent,
          )
        except google.api_core.exceptions.AlreadyExists:
          request = ListIntentsRequest(
            parent=self.parent,
          )
          for intent in self.client.list_intents(request=request):
            if intent.display_name == self._display_name:
              request = GetIntentRequest(
                  name=intent.name,
              )
              self._intent = self.client.get_intent(request=request)
              break


class PageDelegator(ClientDelegator):

    _CLIENT_CLASS = PagesClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller)
        self._display_name = kwargs['display_name']

    @property
    def page(self):
        if not self._page:
            raise RuntimeError('Page not yet created')
        return self._page

    def initialize(self, ):

        try:
        #   training_phrases = []
        #   for training_phrase_text in training_phrases_text:
        #     training_phrase = Intent.TrainingPhrase({
        #         'parts':[{
        #             'text': f'{training_phrase_text}'
        #         }],
        #         'id':'',
        #         'repeat_count':1
        #     })
        #     training_phrases.append(training_phrase)

        #   intent = Intent({
        #       'display_name':self._display_name,
        #       'training_phrases':training_phrases,
        #   })

          self._page = self.client.create_page(
              parent=self.parent,
              page=page,
          )
        except google.api_core.exceptions.AlreadyExists:
          request = PageIntentsRequest(
            parent=self.parent
          )
          for page in self.client.list_pages(request=request):
            if page.display_name == self._display_name:
              request = GetPageRequest(
                  name=page.name,
              )
              self._page = self.client.get_page(request=request)
              break


class WebhookSample(DialogflowSample):

    _AGENT_DISPLAY_NAME = 'Webhook Agent 1'
    _WEBHOOK_DISPLAY_NAME = 'Webhook 1'
    _WEBHOOK_URI = 'https://us-central1-dialogflow-dev-15.cloudfunctions.net/dialogflow-webhook-set-param'
    _INTENT_DISPLAY_NAME = 'go-to-example-page'
    _INTENT_TRAINING_PHRASES_TEXT = ['trigger intent', 'trigger the intent']
    _PAGE_DISPLAY_NAME = 'Main Page'

    def __init__(self, quota_project_id=None):
      self.auth_delegator = AuthDelegator(self, quota_project_id=quota_project_id)
      self.agent_delegator = AgentDelegator(self, display_name=self._AGENT_DISPLAY_NAME)
      self.webhook_delegator = WebhookDelegator(self, display_name=self._WEBHOOK_DISPLAY_NAME, uri=self._WEBHOOK_URI)
      self.intent_delegator = IntentDelegator(self, display_name=self._INTENT_DISPLAY_NAME)
      self.page_delegator = PageDelegator(self, display_name=self._INTENT_DISPLAY_NAME)

    def initialize(self):
      self.agent_delegator.initialize()
      self.webhook_delegator.initialize()
      self.intent_delegator.initialize(self._INTENT_TRAINING_PHRASES_TEXT)
      


if __name__ == "__main__":
    sample = WebhookSample(quota_project_id='dialogflow-dev-14')
    sample.initialize()
    print(sample.intent_delegator.intent)
    # print(f'Agent initialized: https://dialogflow.cloud.google.com/cx/{sample.start_flow}')