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

"""Dialogflow Pages API interactions."""

import dialogflow_sample as ds
import google.api_core.exceptions
import google.cloud.dialogflowcx as cx

from .client_delegator import ClientDelegator


class PageDelegator(ClientDelegator):
    """Class for organizing interactions with the Dialogflow Pages API."""

    _CLIENT_CLASS = cx.PagesClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        self._page = None
        self._entry_fulfillment = None
        super().__init__(controller, **kwargs)

    @property
    def page(self):
        """Page set in Dialogflow."""
        if not self._page:
            raise RuntimeError("Page not yet created")
        return self._page

    @property
    def parent(self):
        """Accesses the parent of page; equivalent to the start_flow."""
        return self.controller.start_flow

    @property
    def entry_fulfillment(self):
        """Accesses the entry fullfillment set for this page."""
        return self._entry_fulfillment

    def setup(self):
        """Initializes the page delegator."""
        page = cx.Page(
            display_name=self.display_name,
            entry_fulfillment=self.entry_fulfillment,
        )
        try:
            self._page = self.client.create_page(
                parent=self.controller.start_flow,
                page=page,
            )
        except google.api_core.exceptions.AlreadyExists:
            request = cx.ListPagesRequest(parent=self.parent)
            for curr_page in self.client.list_pages(request=request):
                if curr_page.display_name == self.display_name:
                    request = cx.GetPageRequest(
                        name=curr_page.name,
                    )
                    self._page = self.client.get_page(request=request)
                    return

    def tear_down(self, force=True):
        """Destroys the Dialogflow page."""
        request = cx.DeletePageRequest(name=self.page.name, force=force)
        try:
            self.client.delete_page(request=request)
            self._page = None
        except google.api_core.exceptions.NotFound:
            pass

    def append_transition_route(
        self, target_page, intent=None, condition=None, trigger_fulfillment=None
    ):
        """Appends a transition route to the page."""
        transition_route = cx.TransitionRoute(
            condition=condition,
            trigger_fulfillment=trigger_fulfillment,
            intent=intent,
            target_page=target_page,
        )
        self.page.transition_routes.append(transition_route)
        self.client.update_page(page=self.page)

    def add_parameter(self, display_name, entity_type, fill_behavior, **kwargs):
        """Adds a form parameter to the page."""
        parameter = cx.Form.Parameter(
            display_name=display_name,
            entity_type=entity_type,
            fill_behavior=fill_behavior,
            **kwargs
        )
        for page_idx, curr_parameter in enumerate(self.page.form.parameters):
            if curr_parameter.display_name == display_name:
                self.page.form.parameters[page_idx] = parameter
                return
        self.page.form.parameters.append(parameter)


class StartPageDelegator(PageDelegator):
    """Special delegator necessary when the start page is a transition target."""

    @property
    def page(self):
        """Mock out the page attribute with the expected name for this special case."""
        return cx.Page(name=self.controller.start_flow_delegator.start_page_name)


class FulfillmentPageDelegator(PageDelegator):
    """Class for organizing interactions with the Dialogflow Pages API with fulfillments."""

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        self._entry_fulfillment_text = kwargs.pop("entry_fulfillment_text")
        self._webhook_delegator = kwargs.pop("webhook_delegator", None)
        self._tag = kwargs.pop("tag", None)
        super().__init__(controller, **kwargs)

    def setup(self):
        """Initializes the fulfillment page delegator."""
        webhook_name = (
            self._webhook_delegator.webhook.name if self._webhook_delegator else None
        )
        self._entry_fulfillment = cx.Fulfillment(
            {
                "messages": [
                    cx.ResponseMessage(
                        text=cx.ResponseMessage.Text(
                            text=[self._entry_fulfillment_text]
                        )
                    )
                ],
                "webhook": webhook_name,
                "tag": self._tag,
            }
        )
        super().setup()
