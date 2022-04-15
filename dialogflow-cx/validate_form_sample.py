from google.cloud.dialogflowcx import Fulfillment, Form, ResponseMessage, Page
import webhook.main as wh
from utilities import RequestMock
import sample_base as sb


def get_expected_response(tag, input_text):
    return "What is your age?"


def build_fulfillment(text=None, webhook=None, tag=None):
    return Fulfillment(
        webhook=webhook,
        tag=tag,
        messages=[ResponseMessage(text=ResponseMessage.Text(text=text))],
    )


class ValidateFormSample(sb.DialogflowSample):

    _WEBHOOK_DISPLAY_NAME = "Validate form"
    _INTENT_DISPLAY_NAME = "go-to-example-page"
    _INTENT_TRAINING_PHRASES_TEXT = ["trigger intent", "trigger the intent"]
    _PAGE_DISPLAY_NAME = "Main Page"
    _PAGE_ENTRY_FULFILLMENT_TEXT = f"Entering {_PAGE_DISPLAY_NAME}"
    _PAGE_WEBHOOK_ENTRY_TAG = "validate_form"

    TEST_CASES = {
        "Test Case 0": {
            "input_text": ["trigger_intent", "21"],
            "expected_response_text": [
                [_PAGE_ENTRY_FULFILLMENT_TEXT, "What is your age?"],
                ["Form Filled", "Valid age"],
            ],
            "expected_exception": None,
        },
        "Test Case 1": {
            "input_text": ["trigger_intent", "-1"],
            "expected_response_text": [
                [_PAGE_ENTRY_FULFILLMENT_TEXT, "What is your age?"],
                ["Form Filled", "Age -1 not valid (must be positive)"],
            ],
            "expected_exception": sb.DialogflowTestCaseFailure,
        },
    }

    def __init__(
        self,
        project_id=None,
        quota_project_id=None,
        webhook_uri=None,
        agent_display_name=None,
    ):
        self.auth_delegator = sb.AuthDelegator(
            self,
            project_id=project_id,
            quota_project_id=quota_project_id,
            credentials=None,
        )
        self.agent_delegator = sb.AgentDelegator(self, display_name=agent_display_name)
        self.webhook_delegator = sb.WebhookDelegator(
            self, display_name=self._WEBHOOK_DISPLAY_NAME, uri=webhook_uri
        )
        self.intent_delegator = sb.IntentDelegator(
            self, display_name=self._INTENT_DISPLAY_NAME
        )
        self.page_delegator = sb.FulfillmentPageDelegator(
            self,
            display_name=self._PAGE_DISPLAY_NAME,
            entry_fulfillment_text=self._PAGE_ENTRY_FULFILLMENT_TEXT,
        )
        self.start_flow_delegator = sb.StartFlowDelegator(self)
        self.start_page_delegator = sb.StartPageDelegator(self)

        self.test_case_delegators = {}
        for display_name, test_config in self.TEST_CASES.items():
            turn_0 = sb.Turn(
                test_config["input_text"][0],
                test_config["expected_response_text"][0],
                self.page_delegator,
                self.intent_delegator,
            )
            turn_1 = sb.Turn(
                test_config["input_text"][1],
                test_config["expected_response_text"][1],
                self.start_page_delegator,
            )
            conversation_turns = [turn_0, turn_1]

            self.test_case_delegators[display_name] = sb.TestCaseDelegator(
                self,
                is_webhook_enabled=True,
                display_name=display_name,
                conversation_turns=conversation_turns,
                expected_exception=test_config["expected_exception"],
            )

    def initialize(self):
        self.agent_delegator.initialize()
        self.webhook_delegator.initialize()
        self.intent_delegator.initialize(self._INTENT_TRAINING_PHRASES_TEXT)
        self.page_delegator.initialize()
        self.start_flow_delegator.initialize()
        self.start_flow_delegator.append_transition_route(
            target_page=self.page_delegator.page.name,
            intent=self.intent_delegator.intent.name,
        )
        self.page_delegator.add_parameter(
            display_name="age",
            required=True,
            entity_type="projects/-/locations/-/agents/-/entityTypes/sys.number",
            fill_behavior=Form.Parameter.FillBehavior(
                initial_prompt_fulfillment=build_fulfillment(text=["What is your age?"])
            ),
            default_value=None,
            redact=False,
            is_list=False,
        )
        self.page_delegator.append_transition_route(
            target_page=self.start_flow_delegator.start_page_name,
            condition="$page.params.status = FINAL",
            trigger_fulfillment=build_fulfillment(
                webhook=self.webhook_delegator.webhook.name,
                tag=self._PAGE_WEBHOOK_ENTRY_TAG,
                text=["Form Filled"],
            ),
        )
        for test_case_delegator in self.test_case_delegators.values():
            test_case_delegator.initialize()

    def tear_down(self):
        for test_case_delegator in self.test_case_delegators.values():
            test_case_delegator.tear_down()
        self.page_delegator.tear_down()
        self.start_flow_delegator.tear_down()
        self.intent_delegator.tear_down()
        self.webhook_delegator.tear_down()
        self.agent_delegator.tear_down()


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Setup Dialogflow CX basic webhook sample"
    )
    parser.add_argument(
        "--agent-display-name",
        help="Display name of the Dialogflow CX agent",
        required=True,
    )
    parser.add_argument(
        "--webhook-uri",
        help="Webhook URL for the Dialogflow CX to use. Format: https://<region>-<project_id>.cloudfunctions.net/<webhook_name>",
        required=True,
    )
    parser.add_argument(
        "--project-id",
        help="Google Cloud project to create/use Dialogflow CX in",
        required=True,
    )
    parser.add_argument(
        "--quota_project-id",
        help="Quota project, if different from project-id",
        default=None,
    )

    sample = ValidateFormSample(**vars(parser.parse_args()))
    sample.initialize()
    for test_case_delegator in sample.test_case_delegators.values():
        if test_case_delegator.expected_exception:
            continue
        else:
            test_case_delegator.run_test_case()
    sample.tear_down()
