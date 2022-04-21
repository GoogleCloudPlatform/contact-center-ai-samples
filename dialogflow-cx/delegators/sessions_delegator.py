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

"""Dialogflow TestCase API interactions."""

import uuid

import dialogflow_sample as ds
import google.cloud.dialogflowcx as cx
from utilities import retry_call

from .client_delegator import ClientDelegator


class SessionsDelegator(ClientDelegator):
    """Class for organizing interactions with the Dialogflow TestCases API."""

    _CLIENT_CLASS = cx.SessionsClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        self.language_code = kwargs.pop("language_code", "en")
        super().__init__(controller, **kwargs)

    def detect_intent(
        self,
        text,
        drop_none_params=True,
        **kwargs,
    ):
        """Run detect_intent for a session against an Agent."""
        parameters = kwargs.pop("parameters", {})
        session_id = kwargs.pop("session_id", str(uuid.uuid1()))
        current_page = kwargs.pop(
            "current_page", self.controller.start_flow_delegator.start_page_name
        )

        request = cx.DetectIntentRequest(
            session=f"{self.controller.agent_delegator.agent.name}/sessions/{session_id}",
            query_input=cx.QueryInput(
                text=cx.TextInput(
                    text=text,
                ),
                language_code=self.language_code,
            ),
            query_params=cx.QueryParameters(
                parameters=parameters,
                current_page=current_page,
            ),
        )

        with retry_call(self.client.detect_intent, request) as response:
            responses = [
                x.text.text[0] for x in response.query_result.response_messages
            ]
            current_page = response.query_result.current_page.name
            parameters = response.query_result.parameters
            if parameters is None:
                parameters = {}
            else:
                parameters = dict(parameters)

        # Parameters that are "None" are removed from the session.
        #  drop_none_params=True performs the same behavior client-side,
        #  to stay in-sync
        if drop_none_params:
            parameters = {
                key: val for key, val in parameters.items() if val is not None
            }

        return responses, current_page, parameters
