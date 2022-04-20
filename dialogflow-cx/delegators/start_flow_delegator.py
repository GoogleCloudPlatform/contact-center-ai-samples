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

"""Dialogflow Flows API interactions."""

import dialogflow_sample as ds
import google.cloud.dialogflowcx as cx

from .client_delegator import ClientDelegator


class StartFlowDelegator(ClientDelegator):
    """Class for organizing interactions with the Dialogflow Flows API."""

    _CLIENT_CLASS = cx.FlowsClient

    def __init__(self, controller: ds.DialogflowSample) -> None:
        super().__init__(controller)
        self._flow = None

    @property
    def flow(self):
        """Start Flow set in Dialogflow."""
        if not self._flow:
            raise RuntimeError("Flow not yet created")
        return self._flow

    def setup(self):
        """Initializes the start flow delegator."""
        flow_name = self.controller.start_flow
        self._flow = self.client.get_flow(name=flow_name)

    def append_transition_route(self, target_page, intent):
        """Appends a transition route to the flow."""
        self.flow.transition_routes.append(
            cx.TransitionRoute(
                intent=intent,
                target_page=target_page,
            )
        )
        self.client.update_flow(flow=self.flow)

    def tear_down(self):
        """Removes the appended transition routes; required to delete agent."""
        self.flow.transition_routes = self.flow.transition_routes[:1]
        self.client.update_flow(flow=self.flow)

    @property
    def start_page_name(self):
        """Gets start page name based on start flow name."""
        return f"{self.flow.name}/pages/START_PAGE"
