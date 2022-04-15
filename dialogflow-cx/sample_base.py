import json
import os
import time

import google.api_core.exceptions
import google.auth
from google.auth import identity_pool
from google.cloud.dialogflowcx import (
    Agent,
    AgentsClient,
    BatchDeleteTestCasesRequest,
    ConversationTurn,
    DeleteAgentRequest,
    DeleteIntentRequest,
    DeletePageRequest,
    DeleteWebhookRequest,
    FlowsClient,
    Form,
    Fulfillment,
    GetAgentRequest,
    GetIntentRequest,
    GetPageRequest,
    GetTestCaseRequest,
    GetWebhookRequest,
    Intent,
    IntentsClient,
    ListAgentsRequest,
    ListIntentsRequest,
    ListPagesRequest,
    ListTestCasesRequest,
    ListWebhooksRequest,
    Page,
    PagesClient,
    QueryInput,
    ResponseMessage,
    RunTestCaseRequest,
    TestCase,
    TestCasesClient,
    TestConfig,
    TestResult,
    TextInput,
    TransitionRoute,
    Webhook,
    WebhooksClient,
)
from google.oauth2 import service_account


class DialogflowTestCaseFailure(Exception):
    """Exception to raise when a test case fails"""


class DialogflowSample:
    """Base class for samples"""

    def set_auth_delegator(self, auth_delegator):
        self._auth_delegator = auth_delegator

    def set_agent_delegator(self, agent_delegator):
        self._agent_delegator = agent_delegator

    @property
    def auth_delegator(self):
        return self._auth_delegator

    @property
    def agent_delegator(self):
        return self._agent_delegator

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

    _CLIENT_CLASS = object  # Override in subclass

    def __init__(self, controller: DialogflowSample, client=None, display_name=None):
        self.controller = controller
        self._client = client
        self._display_name = display_name

    @property
    def client_options(self):
        return {"api_endpoint": f"{self.controller.location}-dialogflow.googleapis.com"}

    @property
    def client(self):
        if self._client is None:
            self._client = self._CLIENT_CLASS(
                client_options=self.client_options,
                credentials=self.controller.auth_delegator.credentials,
            )
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

    _DEFAULT_LANGUAGE_CODE = "en"
    _DEFAULT_TIME_ZONE = "America/Los_Angeles"
    _CLIENT_CLASS = AgentsClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self.default_language_code = kwargs.get(
            "default_language_code", self._DEFAULT_LANGUAGE_CODE
        )
        self.time_zone = kwargs.get("time_zone", self._DEFAULT_TIME_ZONE)

    def initialize(self):
        """Initializes an agent to use for the sample."""
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

    def tear_down(self):
        request = DeleteAgentRequest(name=self.agent.name)
        try:
            self.client.delete_agent(request=request)
        except google.api_core.exceptions.NotFound:
            pass

    @property
    def parent(self):
        return f"projects/{self.controller.project_id}/locations/{self.controller.location}"

    @property
    def agent(self):
        if not self._agent:
            raise RuntimeError("Agent not yet created")
        return self._agent

    @property
    def start_flow(self):
        return self.agent.start_flow


def get_credentials(quota_project_id=None):

    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    with open(credentials_path, "r", encoding="utf8") as f:
        credentials_data = f.read()
        credentials_dict = json.loads(credentials_data)

    if "client_email" in credentials_dict:
        return service_account.Credentials.from_service_account_file(credentials_path)

    if "audience" in credentials_dict:
        return identity_pool.Credentials.from_info(credentials_dict)

    return google.auth.default(quota_project_id=quota_project_id)[0]


class AuthDelegator:

    _DEFAULT_LOCATION = "global"

    def __init__(
        self,
        controller: DialogflowSample,
        project_id=None,
        quota_project_id=None,
        credentials=None,
        **kwargs,
    ):
        self.location = kwargs.get("location", self._DEFAULT_LOCATION)
        self.project_id = project_id
        self.controller = controller
        if not quota_project_id:
            quota_project_id = project_id
        self.quota_project_id = quota_project_id
        self.credentials = (
            credentials
            if credentials
            else get_credentials(quota_project_id=quota_project_id)
        )


class WebhookDelegator(ClientDelegator):

    _CLIENT_CLASS = WebhooksClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        self._uri = kwargs.pop("uri")
        super().__init__(controller, **kwargs)

    @property
    def webhook(self):
        if not self._webhook:
            raise RuntimeError("Webhook not yet created")
        return self._webhook

    def initialize(self):
        """Initializes an agent to use for the sample."""
        webhook = Webhook(
            {
                "display_name": self.display_name,
                "generic_web_service": {"uri": self._uri},
            }
        )
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

    def tear_down(self):
        request = DeleteWebhookRequest(name=self.webhook.name)
        try:
            self.client.delete_webhook(request=request)
        except google.api_core.exceptions.NotFound:
            pass


class IntentDelegator(ClientDelegator):

    _CLIENT_CLASS = IntentsClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)

    @property
    def intent(self):
        if not self._intent:
            raise RuntimeError("Intent not yet created")
        return self._intent

    def initialize(self, training_phrases_text):
        # Create an intent-triggered transition into the page:

        training_phrases = []
        for training_phrase_text in training_phrases_text:
            training_phrase = Intent.TrainingPhrase(
                {
                    "parts": [{"text": f"{training_phrase_text}"}],
                    "id": "",
                    "repeat_count": 1,
                }
            )
            training_phrases.append(training_phrase)

        intent = Intent(
            {
                "display_name": self.display_name,
                "training_phrases": training_phrases,
            }
        )
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

    def tear_down(self):
        request = DeleteIntentRequest(name=self.intent.name)
        try:
            self.client.delete_intent(request=request)
        except google.api_core.exceptions.NotFound:
            pass


class PageDelegator(ClientDelegator):

    _CLIENT_CLASS = PagesClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        self._page = None
        self._entry_fulfillment = None
        super().__init__(controller, **kwargs)

    @property
    def page(self):
        if not self._page:
            raise RuntimeError("Page not yet created")
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

            request = ListPagesRequest(parent=self.parent)
            for curr_page in self.client.list_pages(request=request):
                if curr_page.display_name == self.display_name:
                    request = GetPageRequest(
                        name=curr_page.name,
                    )
                    self._page = self.client.get_page(request=request)
                    return

    def tear_down(self, force=True):
        request = DeletePageRequest(name=self.page.name, force=force)
        try:
            self.client.delete_page(request=request)
        except google.api_core.exceptions.NotFound:
            pass

    def append_transition_route(
        self, target_page, intent=None, condition=None, trigger_fulfillment=None
    ):
        transition_route = TransitionRoute(
            condition=condition,
            trigger_fulfillment=trigger_fulfillment,
            intent=intent,
            target_page=target_page,
        )
        self.page.transition_routes.append(transition_route)
        self.client.update_page(page=self.page)

    def add_parameter(
        self,
        display_name,
        entity_type,
        fill_behavior,
        default_value=None,
        redact=False,
        is_list=False,
        required=True,
    ):
        parameter = Form.Parameter(
            display_name=display_name,
            entity_type=entity_type,
            fill_behavior=fill_behavior,
            default_value=default_value,
            redact=redact,
            is_list=is_list,
            required=required,
        )
        self.page.form.parameters.append(parameter)


class StartPageDelegator(PageDelegator):
    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)

    @property
    def page(self):
        return Page(name=self.controller.start_flow_delegator.start_page_name)


class FulfillmentPageDelegator(PageDelegator):
    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        self._entry_fulfillment_text = kwargs.pop("entry_fulfillment_text")
        self._webhook_delegator = kwargs.pop("webhook_delegator", None)
        self._tag = kwargs.pop("tag", None)
        super().__init__(controller, **kwargs)

    def initialize(self):
        webhook_name = (
            self._webhook_delegator.webhook.name if self._webhook_delegator else None
        )
        self._entry_fulfillment = Fulfillment(
            {
                "messages": [
                    ResponseMessage(
                        text=ResponseMessage.Text(text=[self._entry_fulfillment_text])
                    )
                ],
                "webhook": webhook_name,
                "tag": self._tag,
            }
        )
        super().initialize()


class StartFlowDelegator(ClientDelegator):

    _CLIENT_CLASS = FlowsClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        super().__init__(controller)
        self._flow = None

    @property
    def flow(self):
        if not self._flow:
            raise RuntimeError("Flow not yet created")
        return self._flow

    def initialize(self):
        flow_name = self.controller.start_flow
        self._flow = self.client.get_flow(name=flow_name)

    def append_transition_route(self, target_page, intent):
        self.flow.transition_routes.append(
            TransitionRoute(
                intent=intent,
                target_page=target_page,
            )
        )
        self.client.update_flow(flow=self.flow)

    def tear_down(self):
        self.flow.transition_routes = self.flow.transition_routes[:1]
        self.client.update_flow(flow=self.flow)

    @property
    def start_page_name(self):
        return f"{self.flow.name}/pages/START_PAGE"


class Turn:
    def __init__(
        self, user_input, agent_output, page_delegator, triggered_intent_delegator=None
    ):

        self.user_input = user_input
        self.triggered_intent_delegator = triggered_intent_delegator
        self.page_delegator = page_delegator
        self.agent_output = agent_output

    def get_conversation_turn(self, is_webhook_enabled):
        text_responses = [ResponseMessage.Text(text=text) for text in self.agent_output]
        if not self.triggered_intent_delegator:
            triggered_intent = None
        else:
            triggered_intent = self.triggered_intent_delegator.intent
        virtual_agent_output = ConversationTurn.VirtualAgentOutput(
            current_page=self.page_delegator.page,
            triggered_intent=triggered_intent,
            text_responses=text_responses,
        )
        return ConversationTurn(
            virtual_agent_output=virtual_agent_output,
            user_input=ConversationTurn.UserInput(
                is_webhook_enabled=is_webhook_enabled,
                input=QueryInput(
                    text=TextInput(
                        text=self.user_input,
                    )
                ),
            ),
        )


class TestCaseDelegator(ClientDelegator):

    _CLIENT_CLASS = TestCasesClient

    def __init__(self, controller: DialogflowSample, **kwargs) -> None:
        self._is_webhook_enabled = kwargs.pop("is_webhook_enabled", False)
        self._conversation_turns = kwargs.pop("conversation_turns")
        self.expected_exception = kwargs.pop("expected_exception", None)
        self._test_case = None
        super().__init__(controller, **kwargs)

    @property
    def test_case(self):
        if not self._test_case:
            raise RuntimeError("Test Case not yet created")
        return self._test_case

    def initialize(self):

        try:
            self._test_case = self.client.create_test_case(
                parent=self.controller.agent_delegator.agent.name,
                test_case=TestCase(
                    display_name=self.display_name,
                    test_case_conversation_turns=[
                        t.get_conversation_turn(self._is_webhook_enabled)
                        for t in self._conversation_turns
                    ],
                    test_config=TestConfig(flow=self.controller.start_flow),
                ),
            )
        except google.api_core.exceptions.AlreadyExists:
            request = ListTestCasesRequest(parent=self.parent)
            for curr_test_case in self.client.list_test_cases(request=request):
                if curr_test_case.display_name == self.display_name:
                    request = GetTestCaseRequest(
                        name=curr_test_case.name,
                    )
                    self._test_case = self.client.get_test_case(request=request)
                    return

    def tear_down(self):
        request = BatchDeleteTestCasesRequest(
            parent=self.parent,
            names=[self.test_case.name],
        )
        try:
            self.client.batch_delete_test_cases(request=request)
        except google.api_core.exceptions.NotFound:
            pass

    def run_test_case(self, wait=10, max_retries=3):
        retry_count = 0
        result = None
        while retry_count < max_retries:
            time.sleep(wait)
            lro = self.client.run_test_case(
                request=RunTestCaseRequest(name=self.test_case.name)
            )
            while lro.running():
                try:
                    result = lro.result().result
                    agent_response_differences = [
                        conversation_turn.virtual_agent_output.differences
                        for conversation_turn in result.conversation_turns
                    ]
                    print(agent_response_differences, result.test_result)
                    test_case_fail = result.test_result != TestResult.PASSED
                    if any(agent_response_differences) or test_case_fail:
                        raise DialogflowTestCaseFailure(
                            f'Test "{self.test_case.display_name}" failed'
                        )
                    return
                except google.api_core.exceptions.NotFound as e:
                    if str(e) == (
                        "404 com.google.apps.framework.request.NotFoundException: "
                        "NLU model for flow '00000000-0000-0000-0000-000000000000' does not exist. "
                        "Please try again after retraining the flow."
                    ):
                        retry_count += 1
        raise RuntimeError(f"Retry count exceeded: {retry_count}")
