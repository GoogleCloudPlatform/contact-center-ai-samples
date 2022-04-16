import client_delegator as cd
import dialogflow_sample as ds
from google.cloud.dialogflowcx import FlowsClient, TransitionRoute


class StartFlowDelegator(cd.ClientDelegator):

    _CLIENT_CLASS = FlowsClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        super().__init__(controller)
        self._flow = None

    @property
    def flow(self):
        if not self._flow:
            raise RuntimeError("Flow not yet created")
        return self._flow

    def initialize(self):
        flow_name = self.controller.start_flow
        self._flow = self.client.get_flow(name=flow_name)

    def append_transition_route(self, target_page, intent):
        self.flow.transition_routes.append(
            TransitionRoute(
                intent=intent,
                target_page=target_page,
            )
        )
        self.client.update_flow(flow=self.flow)

    def tear_down(self):
        self.flow.transition_routes = self.flow.transition_routes[:1]
        self.client.update_flow(flow=self.flow)

    @property
    def start_page_name(self):
        return f"{self.flow.name}/pages/START_PAGE"
