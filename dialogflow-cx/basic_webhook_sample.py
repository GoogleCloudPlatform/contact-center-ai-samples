import agent_delegator as agd
import auth_delegator as ad
import dialogflow_sample as ds
import intent_delegator as idy
import page_delegator as pd
import start_flow_delegator as sfd
import test_case_delegator as tcd
import turn
import webhook.main as wh
import webhook_delegator as wd
from utilities import RequestMock


def get_expected_response(tag, input_text):
    return wh.extract_text(
        wh.webhook_fcn(
            RequestMock(payload=wh.build_request_dict_basic(tag, input_text))
        )
    )


class BasicWebhookSample(ds.DialogflowSample):

    _WEBHOOK_DISPLAY_NAME = "Webhook 1"
    _INTENT_DISPLAY_NAME = "go-to-example-page"
    _INTENT_TRAINING_PHRASES_TEXT = ["trigger intent", "trigger the intent"]
    _PAGE_DISPLAY_NAME = "Main Page"
    _PAGE_ENTRY_FULFILLMENT_TEXT = f"Entering {_PAGE_DISPLAY_NAME}"
    _PAGE_WEBHOOK_ENTRY_TAG = "basic_webhook"

    TEST_CASES = {
        "Test Case 0": {
            "input_text": _INTENT_TRAINING_PHRASES_TEXT[0],
            "expected_response_text": [
                _PAGE_ENTRY_FULFILLMENT_TEXT,
                get_expected_response(
                    _PAGE_WEBHOOK_ENTRY_TAG, _INTENT_TRAINING_PHRASES_TEXT[0]
                ),
            ],
            "expected_exception": None,
        },
        "Test Case 1": {
            "input_text": _INTENT_TRAINING_PHRASES_TEXT[1],
            "expected_response_text": [
                _PAGE_ENTRY_FULFILLMENT_TEXT,
                get_expected_response(
                    _PAGE_WEBHOOK_ENTRY_TAG, _INTENT_TRAINING_PHRASES_TEXT[1]
                ),
            ],
            "expected_exception": None,
        },
        "Test Case XFAIL": {
            "input_text": "FAIL",
            "expected_response_text": ["FAIL"],
            "expected_exception": tcd.DialogflowTestCaseFailure,
        },
    }

    def __init__(
        self,
        project_id=None,
        quota_project_id=None,
        webhook_uri=None,
        agent_display_name=None,
    ):
        self.set_auth_delegator(
            ad.AuthDelegator(
                self,
                project_id=project_id,
                quota_project_id=quota_project_id,
                credentials=None,
            )
        )
        self.set_agent_delegator(
            agd.AgentDelegator(self, display_name=agent_display_name)
        )
        self.webhook_delegator = wd.WebhookDelegator(
            self, display_name=self._WEBHOOK_DISPLAY_NAME, uri=webhook_uri
        )
        self.intent_delegator = idy.IntentDelegator(
            self, display_name=self._INTENT_DISPLAY_NAME
        )
        self.page_delegator = pd.FulfillmentPageDelegator(
            self,
            display_name=self._PAGE_DISPLAY_NAME,
            entry_fulfillment_text=self._PAGE_ENTRY_FULFILLMENT_TEXT,
            webhook_delegator=self.webhook_delegator,
            tag=self._PAGE_WEBHOOK_ENTRY_TAG,
        )
        self.start_flow_delegator = sfd.StartFlowDelegator(self)

        self.test_case_delegators = {}
        for display_name, test_config in self.TEST_CASES.items():

            curr_turn = turn.Turn(
                test_config["input_text"],
                test_config["expected_response_text"],
                self.page_delegator,
                self.intent_delegator,
            )
            conversation_turns = [curr_turn]

            self.test_case_delegators[display_name] = tcd.TestCaseDelegator(
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
        help=(
            "Webhook URL for the Dialogflow CX to use. "
            "Format: https://<region>-<project_id>.cloudfunctions.net/<webhook_name>"
        ),
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

    sample = BasicWebhookSample(**vars(parser.parse_args()))
    sample.initialize()
    sample.run()
    sample.tear_down()
