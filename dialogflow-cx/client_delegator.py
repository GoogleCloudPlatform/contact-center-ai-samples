import dialogflow_sample as ds


class ClientDelegator:

    _CLIENT_CLASS = object  # Override in subclass

    def __init__(self, controller: ds.DialogflowSample, client=None, display_name=None):
        self.controller = controller
        self._client = client
        self._display_name = display_name

    @property
    def client_options(self):
        return {"api_endpoint": f"{self.controller.location}-dialogflow.googleapis.com"}

    @property
    def client(self):
        if self._client is None:
            self._client = self._CLIENT_CLASS(
                client_options=self.client_options,
                credentials=self.controller.auth_delegator.credentials,
            )
        return self._client

    @property
    def parent(self):
        return self.controller.agent_delegator.agent.name

    @property
    def display_name(self):
        return self._display_name

    def initialize(self):
        pass
