import client_delegator as cd
import dialogflow_sample as ds
import google.api_core.exceptions
from google.cloud.dialogflowcx import (
    DeletePageRequest,
    Form,
    Fulfillment,
    GetPageRequest,
    ListPagesRequest,
    Page,
    PagesClient,
    ResponseMessage,
    TransitionRoute,
)


class PageDelegator(cd.ClientDelegator):

    _CLIENT_CLASS = PagesClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        self._page = None
        self._entry_fulfillment = None
        super().__init__(controller, **kwargs)

    @property
    def page(self):
        if not self._page:
            raise RuntimeError("Page not yet created")
        return self._page

    @property
    def parent(self):
        return self.controller.start_flow

    @property
    def entry_fulfillment(self):
        return self._entry_fulfillment

    def initialize(self):

        page = Page(
            display_name=self.display_name,
            entry_fulfillment=self.entry_fulfillment,
        )
        try:
            self._page = self.client.create_page(
                parent=self.controller.start_flow,
                page=page,
            )
        except google.api_core.exceptions.AlreadyExists:

            request = ListPagesRequest(parent=self.parent)
            for curr_page in self.client.list_pages(request=request):
                if curr_page.display_name == self.display_name:
                    request = GetPageRequest(
                        name=curr_page.name,
                    )
                    self._page = self.client.get_page(request=request)
                    return

    def tear_down(self, force=True):
        request = DeletePageRequest(name=self.page.name, force=force)
        try:
            self.client.delete_page(request=request)
            self._page = None
        except google.api_core.exceptions.NotFound:
            pass

    def append_transition_route(
        self, target_page, intent=None, condition=None, trigger_fulfillment=None
    ):
        transition_route = TransitionRoute(
            condition=condition,
            trigger_fulfillment=trigger_fulfillment,
            intent=intent,
            target_page=target_page,
        )
        self.page.transition_routes.append(transition_route)
        self.client.update_page(page=self.page)

    def add_parameter(
        self,
        display_name,
        entity_type,
        fill_behavior,
        default_value=None,
        redact=False,
        is_list=False,
        required=True,
    ):
        parameter = Form.Parameter(
            display_name=display_name,
            entity_type=entity_type,
            fill_behavior=fill_behavior,
            default_value=default_value,
            redact=redact,
            is_list=is_list,
            required=required,
        )
        self.page.form.parameters.append(parameter)


class StartPageDelegator(PageDelegator):
    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)

    @property
    def page(self):
        return Page(name=self.controller.start_flow_delegator.start_page_name)


class FulfillmentPageDelegator(PageDelegator):
    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        self._entry_fulfillment_text = kwargs.pop("entry_fulfillment_text")
        self._webhook_delegator = kwargs.pop("webhook_delegator", None)
        self._tag = kwargs.pop("tag", None)
        super().__init__(controller, **kwargs)

    def initialize(self):
        webhook_name = (
            self._webhook_delegator.webhook.name if self._webhook_delegator else None
        )
        self._entry_fulfillment = Fulfillment(
            {
                "messages": [
                    ResponseMessage(
                        text=ResponseMessage.Text(text=[self._entry_fulfillment_text])
                    )
                ],
                "webhook": webhook_name,
                "tag": self._tag,
            }
        )
        super().initialize()
