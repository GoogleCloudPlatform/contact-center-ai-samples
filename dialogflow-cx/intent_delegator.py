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

"""Dialogflow Intents API interactions."""

from typing import List

import client_delegator as cd
import dialogflow_sample as ds
import google.api_core.exceptions
from google.cloud.dialogflowcx import (
    DeleteIntentRequest,
    GetIntentRequest,
    Intent,
    IntentsClient,
    ListIntentsRequest,
)


class IntentDelegator(cd.ClientDelegator):
    """Class for organizing interactions with the Dialogflow Intents API."""

    _CLIENT_CLASS = IntentsClient

    def __init__(
        self, controller: ds.DialogflowSample, training_phrases: List[str], **kwargs
    ) -> None:
        self._intent = None
        self.training_phrases = training_phrases
        super().__init__(controller, **kwargs)

    @property
    def intent(self):
        """Intent set in Dialogflow."""
        if not self._intent:
            raise RuntimeError("Intent not yet created")
        return self._intent

    def initialize(self):
        """Initializes the intent delegator."""
        training_phrases = []
        for training_phrase_text in self.training_phrases:
            training_phrase = Intent.TrainingPhrase(
                {
                    "parts": [{"text": f"{training_phrase_text}"}],
                    "id": "",
                    "repeat_count": 1,
                }
            )
            training_phrases.append(training_phrase)

        intent = Intent(
            {
                "display_name": self.display_name,
                "training_phrases": training_phrases,
            }
        )
        try:
            self._intent = self.client.create_intent(
                parent=self.parent,
                intent=intent,
            )
        except google.api_core.exceptions.AlreadyExists:
            request = ListIntentsRequest(
                parent=self.parent,
            )
            for intent in self.client.list_intents(request=request):
                if intent.display_name == self.display_name:
                    request = GetIntentRequest(
                        name=intent.name,
                    )
                    self._intent = self.client.get_intent(request=request)
                    return

    def tear_down(self):
        request = DeleteIntentRequest(name=self.intent.name)
        try:
            self.client.delete_intent(request=request)
            self._intent = None
        except google.api_core.exceptions.NotFound:
            pass
