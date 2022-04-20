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

import client_delegator as cd
import dialogflow_sample as ds
from google.cloud.dialogflowcx import (
    DetectIntentRequest,
    QueryInput,
    QueryParameters,
    SessionsClient,
    TextInput,
)
from utilities import retry_call


class SessionsDelegator(cd.ClientDelegator):
    """Class for organizing interactions with the Dialogflow TestCases API."""

    _CLIENT_CLASS = SessionsClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)

    def detect_intent(
        self,
        text,
        current_page=None,
        session_id=None,
        parameters=None,
    ):
        """Run detect_intent for a session against an Agent."""

        if parameters is None:
            parameters = {}

        if not session_id:
            session_id = str(uuid.uuid1())

        if not current_page:
            current_page = self.controller.start_flow_delegator.start_page_name

        request = DetectIntentRequest(
            session=f"{self.controller.agent_delegator.agent.name}/sessions/{session_id}",
            query_input=QueryInput(
                text=TextInput(
                    text=text,
                ),
            ),
            query_params=QueryParameters(
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
        return responses, current_page, parameters
