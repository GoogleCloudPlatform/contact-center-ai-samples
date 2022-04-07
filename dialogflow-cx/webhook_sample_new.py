import time

from google.cloud.dialogflowcx import AgentsClient, Agent, ListAgentsRequest, GetAgentRequest
from google.cloud.dialogflowcx import Webhook, WebhooksClient, ListWebhooksRequest, GetWebhookRequest
from google.cloud.dialogflowcx import Intent, IntentsClient, ListIntentsRequest, GetIntentRequest
from google.cloud.dialogflowcx import Page, PagesClient, ListPagesRequest, GetPageRequest, Fulfillment, ResponseMessage
from google.cloud.dialogflowcx import FlowsClient, TransitionRoute
from google.cloud.dialogflowcx import TestCasesClient, TestCase, TestConfig, ConversationTurn, QueryInput, TextInput, ListTestCasesRequest, GetTestCaseRequest, RunTestCaseRequest, TestResult

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

    def __init__(self, controller: DialogflowSample, client=None, display_name=None):
        self.controller = controller
        self._client = client
        self._display_name = display_name

    @property
    def client_options(self):
        return {"api_endpoint": f'{self.controller.location}-dialogflow.googleapis.com'}

    @property
    def client(self):
      if self._client is None: 
        self._client = self._CLIENT_CLASS(client_options=self.client_options, credentials=self.controller.auth_delegator.credentials)
      return self._client

    @property
    def parent(self):
        return self.controller.agent_delegator.agent.name

    @property
    def display_name(self):
        return self._display_name

    def initialize(self):
      pass


class AgentDelegator(ClientDelegator):

    _DEFAULT_LANGUAGE_CODE = 'en'
    _DEFAULT_TIME_ZONE = 'America/Los_Angeles'
    _CLIENT_CLASS = AgentsClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
      super().__init__(controller, **kwargs)
      self.default_language_code = kwargs.get('default_language_code', self._DEFAULT_LANGUAGE_CODE)
      self.time_zone = kwargs.get('time_zone', self._DEFAULT_TIME_ZONE)

    def initialize(self):
        '''Initializes an agent to use for the sample.'''
        try:
          agent = Agent(
              display_name=self.display_name,
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
            if agent.display_name == self.display_name:
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
        print(quota_project_id)
        self.credentials, self.project_id = google.auth.default(quota_project_id=quota_project_id)
        self.location = kwargs.get('location', self._DEFAULT_LOCATION)


class WebhookDelegator(ClientDelegator):

    _CLIENT_CLASS = WebhooksClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        self._uri = kwargs.pop('uri')
        super().__init__(controller, **kwargs)


    @property
    def webhook(self):
        if not self._webhook:
            raise RuntimeError('Webhook not yet created')
        return self._webhook

    def initialize(self):
        '''Initializes an agent to use for the sample.'''
        webhook = Webhook({
            'display_name': self.display_name,
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
            if webhook.display_name == self.display_name:
              request = GetWebhookRequest(
                  name=webhook.name,
              )
              self._webhook = self.client.get_webhook(request=request)
              break


class IntentDelegator(ClientDelegator):

    _CLIENT_CLASS = IntentsClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)

    @property
    def intent(self):
        if not self._intent:
            raise RuntimeError('Intent not yet created')
        return self._intent

    def initialize(self, training_phrases_text):
        # Create an intent-triggered transition into the page:

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
            'display_name':self.display_name,
            'training_phrases':training_phrases,
        })
        try:
          self._intent = self.client.create_intent(
              parent=self.parent,
              intent=intent,
          )
        except google.api_core.exceptions.AlreadyExists:
          request = ListIntentsRequest(
            parent=self.parent,
          )
          for intent in self.client.list_intents(request=request):
            if intent.display_name == self.display_name:
              request = GetIntentRequest(
                  name=intent.name,
              )
              self._intent = self.client.get_intent(request=request)
              return


class PageDelegator(ClientDelegator):

    _CLIENT_CLASS = PagesClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        self._page = None
        self._entry_fulfillment = None
        super().__init__(controller, **kwargs)

    @property
    def page(self):
        if not self._page:
            raise RuntimeError('Page not yet created')
        return self._page

    @property
    def parent(self):
        return self.controller.start_flow

    @property
    def entry_fulfillment(self):
        return self._entry_fulfillment

    def initialize(self):

      page = Page(
          display_name=self.display_name,
          entry_fulfillment=self.entry_fulfillment,
      )
      try:
        self._page = self.client.create_page(
            parent=self.controller.start_flow,
            page=page,
        )
      except google.api_core.exceptions.AlreadyExists:

        request = ListPagesRequest(
          parent=self.parent
        )
        for curr_page in self.client.list_pages(request=request):
          if curr_page.display_name == self.display_name:
            request = GetPageRequest(
                name=curr_page.name,
            )
            self._page = self.client.get_page(request=request)
            return


class FulfillmentPageDelegator(PageDelegator):

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        self._entry_fulfillment_text = kwargs.pop('entry_fulfillment_text')
        self._webhook_delegator = kwargs.pop('webhook_delegator')
        self._tag = kwargs.pop('tag', None)
        super().__init__(controller, **kwargs)

    def initialize(self):
        webhook_name = self._webhook_delegator.webhook.name if self._webhook_delegator else None
        self._entry_fulfillment = Fulfillment({
            'messages': [
                ResponseMessage(
                    text=ResponseMessage.Text(
                        text=[self._entry_fulfillment_text]
                    )
                )
            ],
            'webhook': webhook_name,
            'tag': self._tag,
        })
        super().initialize()


class FlowDelegator(ClientDelegator):

    _CLIENT_CLASS = FlowsClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller)

    def append_transition_route(self, intent_name, target_page_name, flow_name=None):
        if not flow_name:
            flow_name = sample.start_flow

        flow = self.client.get_flow(name=flow_name)
        flow.transition_routes.append(TransitionRoute(
            intent=intent_name,
            target_page=target_page_name,
        ))
        self.client.update_flow(flow=flow)


class TestCaseDelegator(ClientDelegator):

    _CLIENT_CLASS = TestCasesClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        self._is_webhook_enabled = kwargs.pop('is_webhook_enabled', True)
        self._input_text = kwargs.pop('input_text')
        self._response_text = kwargs.pop('response_text')
        self.page_delegator = kwargs.pop('page_delegator')
        self.intent_delegator = kwargs.pop('intent_delegator')
        self._test_case = None
        super().__init__(controller, **kwargs)

    @property
    def test_case(self):
        if not self._test_case:
            raise RuntimeError('Page not yet created')
        return self._test_case

    def initialize(self):
        text_responses = [ResponseMessage.Text(
            text=text
        ) for text in self._response_text]
        virtual_agent_output = ConversationTurn.VirtualAgentOutput(
            current_page=self.page_delegator.page,
            triggered_intent=self.intent_delegator.intent,
            text_responses=text_responses)
        conversation_turn = ConversationTurn(
            virtual_agent_output=virtual_agent_output,
            user_input=ConversationTurn.UserInput(
                is_webhook_enabled=self._is_webhook_enabled,
                input=QueryInput(
                    text=TextInput(
                      text=self._input_text,
                    )
                )
            )
        )

        try:
          self._test_case = self.client.create_test_case(
              parent=self.controller.agent_delegator.agent.name,
              test_case=TestCase(display_name=self.display_name,
              test_case_conversation_turns=[conversation_turn],
              test_config=TestConfig(flow=self.controller.start_flow))
          )
        except google.api_core.exceptions.AlreadyExists:
          request = ListTestCasesRequest(
            parent=self.parent
          )
          for curr_test_case in self.client.list_test_cases(request=request):
            if curr_test_case.display_name == self.display_name:
              request = GetTestCaseRequest(
                  name=curr_test_case.name,
              )
              self._test_case = self.client.get_test_case(request=request)
              return




class WebhookSample(DialogflowSample):

    _AGENT_DISPLAY_NAME = 'Webhook Agent 19'
    _WEBHOOK_DISPLAY_NAME = 'Webhook 1'
    _WEBHOOK_URI = 'https://us-central1-df-terraform-dev04cc.cloudfunctions.net/wh-df-terraform-dev04cc'
    _INTENT_DISPLAY_NAME = 'go-to-example-page'
    _INTENT_TRAINING_PHRASES_TEXT = ['trigger intent', 'trigger the intent']
    _PAGE_DISPLAY_NAME = 'Main Page'
    _PAGE_ENTRY_FULFILLMENT_TEXT=f'Entering {_PAGE_DISPLAY_NAME}'
    _PAGE_WEBHOOK_ENTRY_TAG = 'enter_main_page'
    _TEST_CASE_DISPLAY_NAME = 'Test Case 5'
    # _TEST_RESPONSE_TEXT = ['ERROR']
    _TEST_RESPONSE_TEXT = [_PAGE_ENTRY_FULFILLMENT_TEXT, f'Webhook received: {_INTENT_TRAINING_PHRASES_TEXT[0]} (Tag: {_PAGE_WEBHOOK_ENTRY_TAG})']

    def __init__(self, quota_project_id=None):
      self.auth_delegator = AuthDelegator(self, quota_project_id=quota_project_id)
      self.agent_delegator = AgentDelegator(self, display_name=self._AGENT_DISPLAY_NAME)
      self.webhook_delegator = WebhookDelegator(self, display_name=self._WEBHOOK_DISPLAY_NAME, uri=self._WEBHOOK_URI)
      self.intent_delegator = IntentDelegator(self, display_name=self._INTENT_DISPLAY_NAME)
      self.page_delegator = FulfillmentPageDelegator(self, 
          display_name=self._PAGE_DISPLAY_NAME, 
          entry_fulfillment_text=self._PAGE_ENTRY_FULFILLMENT_TEXT,
          webhook_delegator=self.webhook_delegator,
          tag=self._PAGE_WEBHOOK_ENTRY_TAG,
          )
      self.flow_delegator = FlowDelegator(self)
      self.test_case_delegator = TestCaseDelegator(self, 
          display_name=self._TEST_CASE_DISPLAY_NAME, 
          input_text=self._INTENT_TRAINING_PHRASES_TEXT[0],
          response_text=self._TEST_RESPONSE_TEXT,
          page_delegator=self.page_delegator,
          intent_delegator=self.intent_delegator,
      )

    def initialize(self):
      self.agent_delegator.initialize()
      self.webhook_delegator.initialize()
      self.intent_delegator.initialize(self._INTENT_TRAINING_PHRASES_TEXT)
      self.page_delegator.initialize()
      self.flow_delegator.initialize()
      self.flow_delegator.append_transition_route(
          self.intent_delegator.intent.name,
          self.page_delegator.page.name
      )
      self.test_case_delegator.initialize()

    def run(self, wait=10, max_retries=3):

      retry_count = 0
      result = None
      while retry_count < max_retries:
        time.sleep(wait)
        lro = self.test_case_delegator.client.run_test_case(request=RunTestCaseRequest(name=self.test_case_delegator.test_case.name))
        while lro.running():
          try:
            return lro.result().result
          except google.api_core.exceptions.NotFound as e:
            if str(e) == '404 com.google.apps.framework.request.NotFoundException: NLU model for flow \'00000000-0000-0000-0000-000000000000\' does not exist. Please try again after retraining the flow.':
              retry_count += 1

      if result:
        return result
      else:
        raise RuntimeError(f'Retry count exceeded: {retry_count}')


if __name__ == "__main__":
    sample = WebhookSample(quota_project_id='df-terraform-dev04cc')
    sample.initialize()
    result = sample.run()
    assert not result.conversation_turns[0].virtual_agent_output.differences
    assert result.test_result == TestResult.PASSED
