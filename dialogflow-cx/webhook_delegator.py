import client_delegator as cd
import dialogflow_sample as ds
import google.api_core.exceptions
import google.auth
from google.cloud.dialogflowcx import (
    DeleteWebhookRequest,
    GetWebhookRequest,
    ListWebhooksRequest,
    Webhook,
    WebhooksClient,
)


class WebhookDelegator(cd.ClientDelegator):

    _CLIENT_CLASS = WebhooksClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        self._uri = kwargs.pop("uri")
        super().__init__(controller, **kwargs)

    @property
    def webhook(self):
        if not self._webhook:
            raise RuntimeError("Webhook not yet created")
        return self._webhook

    def initialize(self):
        """Initializes an agent to use for the sample."""
        webhook = Webhook(
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
            request = ListWebhooksRequest(
                parent=self.parent,
            )
            for webhook in self.client.list_webhooks(request=request):
                if webhook.display_name == self.display_name:
                    request = GetWebhookRequest(
                        name=webhook.name,
                    )
                    self._webhook = self.client.get_webhook(request=request)
                    break

    def tear_down(self):
        request = DeleteWebhookRequest(name=self.webhook.name)
        try:
            self.client.delete_webhook(request=request)
            self._webhook = None
        except google.api_core.exceptions.NotFound:
            pass
