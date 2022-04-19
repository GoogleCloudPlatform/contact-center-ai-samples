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

"""Module for the base class for all Dialogflow CX samples."""


class UnexpectedResponseFailure(AssertionError):
    """Exception to raise when a test case fails"""

class TestCaseFailure(AssertionError):
    """Exception to raise when a test case fails"""


from typing import Dict

import client_delegator as cd
import time

import google.cloud.dialogflowcx as cx
import uuid


class DialogflowSample:
    """Base class for samples."""

    def __init__(self) -> None:
        self._agent_delegator = None
        self._auth_delegator = None
        self._credentials = None
        self._test_cases_client = None

    def set_auth_delegator(self, auth_delegator):
        """Sets the AuthDelegator for the sample."""
        self._auth_delegator = auth_delegator

    def set_agent_delegator(self, agent_delegator):
        """Sets the AgentDelegator for the sample."""
        self._agent_delegator = agent_delegator

    def set_credentials(self, credentials):
        """Sets the AgentDelegator for the sample."""
        self._credentials = credentials

    @property
    def auth_delegator(self):
        """Accesses the auth_delegator for the sample."""
        return self._auth_delegator

    @property
    def agent_delegator(self):
        """Accesses the agent_delegator for the sample."""
        return self._agent_delegator

    @property
    def credentials(self):
        """Accesses the agent_delegator for the sample."""
        return self._credentials

    @property
    def project_id(self):
        """Accesses the project ID for the sample."""
        return self.auth_delegator.project_id

    @property
    def location(self):
        """Accesses the location ID for the sample."""
        return self.auth_delegator.location

    @property
    def start_flow(self):
        """Accesses the start_flow for the sample."""
        return self.agent_delegator.start_flow

    @property
    def client_options(self):
        """Accesses the client_options for the delegator."""
        return {"api_endpoint": f"{self.location}-dialogflow.googleapis.com"}

    @property
    def test_cases_client(self):
        """Accesses the test_case_delegators for the sample."""
        if self._test_cases_client is None:
            self._test_cases_client = cx.TestCasesClient(
                client_options=self.client_options,
                credentials=self.credentials,
            )
        return self._test_cases_client

    def setup(self, wait=0):
        """Set up sample. Especially, train the start flow."""
        request = cx.TrainFlowRequest(
            name=self.start_flow_delegator.flow.name
        )
        lro = self.start_flow_delegator.client.train_flow(request=request)
        t0 = time.time()
        while lro.running():
            time.sleep(.1)
        time.sleep(wait)

    def run(self, user_text_list, session_id=None, language_code='en', wait=1, parameters=None, current_page=None, quiet=False):
        """Runs a conversation with this agent."""
        time.sleep(wait)

        if parameters is None:
            parameters = {}

        if not session_id:
            session_id = str(uuid.uuid1())

        for text in user_text_list:
            if not quiet:
                print('User: ')
                print(f'  Text: {text}')
                print(f'  Starting Parameters: {parameters}')
                print(f'  Page: {current_page}')
            responses, current_page, parameters = self.sessions_delegator.detect_intent(
                text, 
                parameters=parameters,
                current_page=current_page,
                session_id=session_id,
                language_code=language_code,
            )
            if not quiet:
                print('  Agent:')
                for response in responses:
                    print(f'    Text: {response}')
                print(f'    Ending Parameters: {parameters}')
                print(f'    Ending Page: {current_page}')


    def create_test_case(self, display_name, test_case_conversation_turns, flow=None):
        """Create a test case."""
        if flow is None:
            flow = self.start_flow

        return self.test_cases_client.create_test_case(
            parent=self.agent_delegator.agent.name,
            test_case=cx.TestCase(
                display_name=display_name,
                test_case_conversation_turns=test_case_conversation_turns,
                test_config=cx.TestConfig(flow=flow),
            ),
        )

    def run_test_case(self, test_case):

        lro = self.test_cases_client.run_test_case(
            request=cx.RunTestCaseRequest(name=test_case.name)
        )
        while lro.running():
            time.sleep(.1)
        result = lro.result().result
        agent_response_differences = [
            conversation_turn.virtual_agent_output.differences
            for conversation_turn in result.conversation_turns
        ]

        if any(agent_response_differences):
            raise UnexpectedResponseFailure(agent_response_differences)
        
        final_session_parameters = []
        for conversation_turn in result.conversation_turns:
            print(conversation_turn.virtual_agent_output)
            if conversation_turn.virtual_agent_output.parameters:
                final_session_parameters.append(dict(conversation_turn.virtual_agent_output.parameters))
            else:
                final_session_parameters.append({})
        print(final_session_parameters)


        if result.test_result != cx.TestResult.PASSED:
            raise(TestCaseFailure)
        