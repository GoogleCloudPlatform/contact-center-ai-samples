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

"""Agent Delegator module. Coordinates agent state with Dialogflow."""


import dialogflow_sample as ds
import google.api_core.exceptions
import google.auth
import google.cloud.dialogflowcx as cx

from .client_delegator import ClientDelegator


class AgentDelegator(ClientDelegator):
    """Class for organizing interactions with the Dialogflow Agent API."""

    _DEFAULT_LANGUAGE_CODE = "en"
    _DEFAULT_TIME_ZONE = "America/Los_Angeles"
    _CLIENT_CLASS = cx.AgentsClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)
        self._agent = None
        self.default_language_code = kwargs.get(
            "default_language_code", self._DEFAULT_LANGUAGE_CODE
        )
        self.time_zone = kwargs.get("time_zone", self._DEFAULT_TIME_ZONE)

    def setup(self):
        """Initializes the agent delegator."""
        try:
            agent = cx.Agent(
                display_name=self.display_name,
                default_language_code=self.default_language_code,
                time_zone=self.time_zone,
            )
            request = {"agent": agent, "parent": self.parent}
            self._agent = self.client.create_agent(request=request)
        except google.api_core.exceptions.AlreadyExists:
            request = cx.ListAgentsRequest(
                parent=self.parent,
            )
            for agent in self.client.list_agents(request=request):
                if agent.display_name == self.display_name:
                    request = cx.GetAgentRequest(
                        name=agent.name,
                    )
                    self._agent = self.client.get_agent(request=request)
                    break

    def tear_down(self):
        """Destroys the Dialogflow agent."""
        request = cx.DeleteAgentRequest(name=self.agent.name)
        try:
            self.client.delete_agent(request=request)
            self._agent = None
        except google.api_core.exceptions.NotFound:
            pass

    @property
    def parent(self):
        """Accesses the parent of the agent."""
        return f"projects/{self.controller.project_id}/locations/{self.controller.location}"

    @property
    def agent(self):
        """Agent set in Dialogflow."""
        if not self._agent:
            raise RuntimeError("Agent not yet created")
        return self._agent

    @property
    def start_flow(self):
        """Accesses the start flow of the agent."""
        return self.agent.start_flow
