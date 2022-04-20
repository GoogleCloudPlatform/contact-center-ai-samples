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

"""Dialogflow Webhooks API interactions."""

import dialogflow_sample as ds
import google.api_core.exceptions
import google.auth
import google.cloud.dialogflowcx as cx

from .client_delegator import ClientDelegator


class WebhookDelegator(ClientDelegator):
    """Class for organizing interactions with the Dialogflow Webhooks API."""

    _CLIENT_CLASS = cx.WebhooksClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        self._uri = kwargs.pop("uri")
        self._webhook = None
        super().__init__(controller, **kwargs)

    @property
    def webhook(self):
        """Webhook set in Dialogflow."""
        if not self._webhook:
            raise RuntimeError("Webhook not yet created")
        return self._webhook

    def setup(self):
        """Initializes the webhook delegator."""
        webhook = cx.Webhook(
            {
                "display_name": self.display_name,
                "generic_web_service": {"uri": self._uri},
            }
        )
        try:
            self._webhook = self.client.create_webhook(
                parent=self.parent,
                webhook=webhook,
            )
        except google.api_core.exceptions.AlreadyExists:
            request = cx.ListWebhooksRequest(
                parent=self.parent,
            )
            for webhook in self.client.list_webhooks(request=request):
                if webhook.display_name == self.display_name:
                    request = cx.GetWebhookRequest(
                        name=webhook.name,
                    )
                    self._webhook = self.client.get_webhook(request=request)
                    break

    def tear_down(self):
        """Destroys the Dialogflow webhook."""
        request = cx.DeleteWebhookRequest(name=self.webhook.name)
        try:
            self.client.delete_webhook(request=request)
            self._webhook = None
        except google.api_core.exceptions.NotFound:
            pass
