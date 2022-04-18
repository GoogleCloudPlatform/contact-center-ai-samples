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

"""Dialogflow CX Sample: Entry fullfillment with a webhook."""

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
    """Gets the response expected from the webhook, for a given tag."""
    return wh.extract_text(
        wh.webhook_fcn(
            RequestMock(payload=wh.build_request_dict_basic(tag, input_text))
        )
    )


class BasicWebhookSample(ds.DialogflowSample):
    """Sets up a Dialogflow agent that uses a webhook to provide an entry fulfillment."""

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
        super().__init__()
        if not quota_project_id:
            quota_project_id = project_id
        self.set_auth_delegator(
            ad.AuthDelegator(
                self,
                project_id=project_id,
                quota_project_id=quota_project_id,
            )
        )
        self.set_agent_delegator(
            agd.AgentDelegator(self, display_name=agent_display_name)
        )
        self.webhook_delegator = wd.WebhookDelegator(
            self, display_name=self._WEBHOOK_DISPLAY_NAME, uri=webhook_uri
        )
        self.intent_delegator = idy.IntentDelegator(
            self,
            display_name=self._INTENT_DISPLAY_NAME,
            training_phrases=self._INTENT_TRAINING_PHRASES_TEXT,
        )
        self.page_delegator = pd.FulfillmentPageDelegator(
            self,
            display_name=self._PAGE_DISPLAY_NAME,
            entry_fulfillment_text=self._PAGE_ENTRY_FULFILLMENT_TEXT,
            webhook_delegator=self.webhook_delegator,
            tag=self._PAGE_WEBHOOK_ENTRY_TAG,
        )
        self.start_flow_delegator = sfd.StartFlowDelegator(self)

        for display_name, test_config in self.TEST_CASES.items():

            curr_turn = turn.Turn(
                test_config["input_text"],
                test_config["expected_response_text"],
                self.page_delegator,
                self.intent_delegator,
            )
            conversation_turns = [curr_turn]

            self.add_test_case_delegator(
                display_name,
                tcd.TestCaseDelegator(
                    self,
                    is_webhook_enabled=True,
                    display_name=display_name,
                    conversation_turns=conversation_turns,
                    expected_exception=test_config["expected_exception"],
                ),
            )

    def setup(self):
        """Initializes the sample by communicating with the Dialogflow API."""
        self.agent_delegator.setup()
        self.webhook_delegator.setup()
        self.intent_delegator.setup()
        self.page_delegator.setup()
        self.start_flow_delegator.setup()
        self.start_flow_delegator.append_transition_route(
            target_page=self.page_delegator.page.name,
            intent=self.intent_delegator.intent.name,
        )
        for test_case_delegator in self.test_case_delegators.values():
            test_case_delegator.setup()

    def tear_down(self):
        """Deletes the sample components via the Dialogflow API."""
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
        "--quota-project-id",
        help="Quota project, if different from project-id",
        default=None,
    )

    sample = BasicWebhookSample(**vars(parser.parse_args()))
    sample.setup()
    sample.run()
    sample.tear_down()
