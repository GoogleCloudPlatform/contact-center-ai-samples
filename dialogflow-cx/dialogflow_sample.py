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

    def run(self):
        for test_case_delegator in self.test_case_delegators.values():
            if not test_case_delegator.expected_exception:
                test_case_delegator.run_test_case()
