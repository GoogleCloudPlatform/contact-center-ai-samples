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

"""Module for the base class for API delegators for Dialogflow CX samples."""

import dialogflow_sample as ds


class ClientDelegator:
    """Base class for API delegators for Dialogflow CX samples."""

    _CLIENT_CLASS = object  # Override in subclass

    def __init__(self, controller: ds.DialogflowSample, client=None, display_name=None):
        self.controller = controller
        self._client = client
        self._display_name = display_name

    @property
    def client(self):
        """Accesses the API client for the delegator."""
        if self._client is None:
            self._client = self._CLIENT_CLASS(
                client_options=self.controller.client_options,
                credentials=self.controller.auth_delegator.credentials,
            )
        return self._client

    @property
    def parent(self):
        """Accesses agent name, i.e. the parent for the most delegator components."""
        return self.controller.agent_delegator.agent.name

    @property
    def display_name(self):
        """Accesses the display_name for the delegator."""
        return self._display_name
