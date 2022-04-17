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

"""AgentDelegator module. Coordinates agent state with Dialogflow."""


import client_delegator as cd
import dialogflow_sample as ds
import google.api_core.exceptions
import google.auth
from google.cloud.dialogflowcx import (
    Agent,
    AgentsClient,
    DeleteAgentRequest,
    GetAgentRequest,
    ListAgentsRequest,
)


class AgentDelegator(cd.ClientDelegator):

    _DEFAULT_LANGUAGE_CODE = "en"
    _DEFAULT_TIME_ZONE = "America/Los_Angeles"
    _CLIENT_CLASS = AgentsClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self.default_language_code = kwargs.get(
            "default_language_code", self._DEFAULT_LANGUAGE_CODE
        )
        self.time_zone = kwargs.get("time_zone", self._DEFAULT_TIME_ZONE)

    def initialize(self):
        """Initializes an agent to use for the sample."""
        try:
            agent = Agent(
                display_name=self.display_name,
                default_language_code=self.default_language_code,
                time_zone=self.time_zone,
            )
            request = {"agent": agent, "parent": self.parent}
            self._agent = self.client.create_agent(request=request)
        except google.api_core.exceptions.AlreadyExists:
            request = ListAgentsRequest(
                parent=self.parent,
            )
            for agent in self.client.list_agents(request=request):
                if agent.display_name == self.display_name:
                    request = GetAgentRequest(
                        name=agent.name,
                    )
                    self._agent = self.client.get_agent(request=request)
                    break

    def tear_down(self):
        request = DeleteAgentRequest(name=self.agent.name)
        try:
            self.client.delete_agent(request=request)
            self._agent = None
        except google.api_core.exceptions.NotFound:
            pass

    @property
    def parent(self):
        return f"projects/{self.controller.project_id}/locations/{self.controller.location}"

    @property
    def agent(self):
        if not self._agent:
            raise RuntimeError("Agent not yet created")
        return self._agent

    @property
    def start_flow(self):
        return self.agent.start_flow
