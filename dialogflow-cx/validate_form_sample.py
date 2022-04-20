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

"""Dialogflow CX Sample: Form validation with a webhook."""

import agent_delegator as agd
import auth_delegator as ad
import dialogflow_sample as ds
import intent_delegator as idy
import page_delegator as pd
import sessions_delegator as sd
import start_flow_delegator as sfd
import webhook_delegator as wd
from google.cloud.dialogflowcx import Form, Fulfillment, ResponseMessage
from webhook.main import get_webhook_uri


def build_fulfillment(text=None, webhook=None, tag=None):
    """Helper method that provides a Fulfillment based on text, webhook and tag."""
    return Fulfillment(
        webhook=webhook,
        tag=tag,
        messages=[ResponseMessage(text=ResponseMessage.Text(text=text))],
    )


class ValidateFormSample(ds.DialogflowSample):
    """Sets up a Dialogflow agent that uses a webhook to validate a form parameter."""

    _WEBHOOK_DISPLAY_NAME = "Validate form"
    _INTENT_DISPLAY_NAME = "go-to-example-page"
    _INTENT_TRAINING_PHRASES_TEXT = ["trigger intent", "trigger the intent"]
    _PAGE_DISPLAY_NAME = "Main Page"
    _PAGE_ENTRY_FULFILLMENT_TEXT = f"Entering {_PAGE_DISPLAY_NAME}"
    _PAGE_WEBHOOK_ENTRY_TAG = "validate_form"
    _PAGE_PROMPT = "What is your age?"

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
        )
        self.set_start_flow_delegator(sfd.StartFlowDelegator(self))
        self.set_session_delegator(sd.SessionsDelegator(self))
        self.start_page_delegator = pd.StartPageDelegator(self)

    def setup(self, wait=1):
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
        self.page_delegator.add_parameter(
            display_name="age",
            required=True,
            entity_type="projects/-/locations/-/agents/-/entityTypes/sys.number",
            fill_behavior=Form.Parameter.FillBehavior(
                initial_prompt_fulfillment=build_fulfillment(text=[self._PAGE_PROMPT])
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
        super().setup(wait=wait)

    def tear_down(self):
        """Deletes the sample components via the Dialogflow API."""
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
        "--project-id",
        help="Google Cloud project to create/use Dialogflow CX in",
        required=True,
    )
    parser.add_argument(
        "--quota-project-id",
        help="Quota project, if different from project-id",
        default=None,
    )
    parser.add_argument(
        "--user-input",
        nargs="+",
        help="User text utterances",
        required=False,
        default=[],
    )
    parser.add_argument(
        "--tear-down", action="store_true", help="Destroy the agent after run?"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--webhook-uri",
        help=(
            "Webhook URL for the Dialogflow CX to use. "
            "Format: https://<region>-<project_id>.cloudfunctions.net/<webhook_name>"
        ),
    )
    group.add_argument(
        "--build-uuid", help="Infer the webhook URI from the build_uuid and project id"
    )

    args = vars(parser.parse_args())
    if args["build_uuid"]:
        assert not args["webhook_uri"]
        args["webhook_uri"] = get_webhook_uri(
            args["project_id"], args.pop("build_uuid")
        )

    tear_down = args.pop("tear_down")
    user_input = args.pop("user_input", [])
    sample = ValidateFormSample(**args)
    sample.setup()
    sample.run(user_input)
    if tear_down:
        sample.tear_down()

        # for test_case_delegator in self.test_case_delegators.values():
        #     test_case_delegator.tear_down()
# import test_case_delegator as tcd
# TEST_CASES = {
#     "Test Case 0": {
#         "input_text": ["trigger_intent", "21"],
#         "expected_response_text": [
#             [_PAGE_ENTRY_FULFILLMENT_TEXT, _PAGE_PROMPT],
#             ["Form Filled", "Valid age"],
#         ],
#         "expected_exception": None,
#     },
#     "Test Case 1": {
#         "input_text": ["trigger_intent", "-1"],
#         "expected_response_text": [
#             [_PAGE_ENTRY_FULFILLMENT_TEXT, _PAGE_PROMPT],
#             ["Form Filled", "Age -1 not valid (must be positive)"],
#         ],
#         "expected_exception": tcd.DialogflowTestCaseFailure,
#     },
# }
# for test_case_delegator in self.test_case_delegators.values():
# test_case_delegator.setup()

# for display_name, test_config in self.TEST_CASES.items():
#     turn_0 = turn.Turn(
#         test_config["input_text"][0],
#         test_config["expected_response_text"][0],
#         self.page_delegator,
#         self.intent_delegator,
#     )
#     turn_1 = turn.Turn(
#         test_config["input_text"][1],
#         test_config["expected_response_text"][1],
#         self.start_page_delegator,
#     )
#     conversation_turns = [turn_0, turn_1]

#     self.add_test_case_delegator(
#         display_name,
#         tcd.TestCaseDelegator(
#             self,
#             is_webhook_enabled=True,
#             display_name=display_name,
#             conversation_turns=conversation_turns,
#             expected_exception=test_config["expected_exception"],
#         ),
#     )
