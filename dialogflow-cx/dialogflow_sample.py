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


class DialogflowSample:
    """Base class for samples."""

    def __init__(self) -> None:
        self._agent_delegator = None
        self._auth_delegator = None
        self._credentials = None
        self.test_case_delegators = None

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

    def run(self):
        """Runs the sample test cases that are not intended to fail."""
        for test_case_delegator in self.test_case_delegators.values():
            if not test_case_delegator.expected_exception:
                test_case_delegator.run_test_case()
