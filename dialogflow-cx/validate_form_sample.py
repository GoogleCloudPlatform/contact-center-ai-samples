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

import delegators as dg
import dialogflow_sample as ds
import google.cloud.dialogflowcx as cx
from webhook.main import get_webhook_uri


def build_fulfillment(text=None, webhook=None, tag=None):
    """Helper method that provides a Fulfillment based on text, webhook and tag."""
    return cx.Fulfillment(
        webhook=webhook,
        tag=tag,
        messages=[cx.ResponseMessage(text=cx.ResponseMessage.Text(text=text))],
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
            dg.AuthDelegator(
                self,
                project_id=project_id,
                quota_project_id=quota_project_id,
            )
        )
        self.set_agent_delegator(
            dg.AgentDelegator(self, display_name=agent_display_name)
        )
        self.webhook_delegator = dg.WebhookDelegator(
            self, display_name=self._WEBHOOK_DISPLAY_NAME, uri=webhook_uri
        )
        self.intent_delegator = dg.IntentDelegator(
            self,
            display_name=self._INTENT_DISPLAY_NAME,
            training_phrases=self._INTENT_TRAINING_PHRASES_TEXT,
        )
        self.page_delegator = dg.FulfillmentPageDelegator(
            self,
            display_name=self._PAGE_DISPLAY_NAME,
            entry_fulfillment_text=self._PAGE_ENTRY_FULFILLMENT_TEXT,
        )
        self.set_start_flow_delegator(dg.StartFlowDelegator(self))
        self.set_session_delegator(dg.SessionsDelegator(self))
        self.start_page_delegator = dg.StartPageDelegator(self)

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
            fill_behavior=cx.Form.Parameter.FillBehavior(
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

    parser = argparse.ArgumentParser(description="Setup Validate Form webhook sample")
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
    else:
        print(
            "Agent sample available at: "
            f"https://dialogflow.cloud.google.com/cx/{sample.start_flow_delegator.flow.name}"
        )
