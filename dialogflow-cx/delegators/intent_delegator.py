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

import dialogflow_sample as ds
import google.api_core.exceptions
import google.cloud.dialogflowcx as cx

from .client_delegator import ClientDelegator


class IntentDelegator(ClientDelegator):
    """Class for organizing interactions with the Dialogflow Intents API."""

    _CLIENT_CLASS = cx.IntentsClient

    def __init__(
        self,
        controller: ds.DialogflowSample,
        training_phrases: List[cx.Intent.TrainingPhrase.Part],
        **kwargs,
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

    def get_intent(self):
        """Create and Intent object to be pushed to the API."""
        training_phrases = []
        for training_phrase_text in self.training_phrases:
            training_phrase = cx.Intent.TrainingPhrase(
                {
                    "parts": [{"text": f"{training_phrase_text}"}],
                    "id": "",
                    "repeat_count": 1,
                }
            )
            training_phrases.append(training_phrase)

        return cx.Intent(
            {
                "display_name": self.display_name,
                "training_phrases": training_phrases,
            }
        )

    def setup(self):
        """Initializes the intent delegator."""
        intent = self.get_intent()
        try:
            self._intent = self.client.create_intent(
                parent=self.parent,
                intent=intent,
            )
        except google.api_core.exceptions.AlreadyExists:
            request = cx.ListIntentsRequest(
                parent=self.parent,
            )
            for intent in self.client.list_intents(request=request):
                if intent.display_name == self.display_name:
                    request = cx.GetIntentRequest(
                        name=intent.name,
                    )
                    self._intent = self.client.get_intent(request=request)
                    return

    def tear_down(self):
        """Destroys the Dialogflow intent."""
        request = cx.DeleteIntentRequest(name=self.intent.name)
        try:
            self.client.delete_intent(request=request)
            self._intent = None
        except google.api_core.exceptions.NotFound:
            pass


class AnnotatedIntentDelegator(IntentDelegator):
    """IntentDelegator with annotated spans of text for parameter detection."""

    def __init__(
        self,
        controller: ds.DialogflowSample,
        training_phrases: List[cx.Intent.TrainingPhrase.Part],
        parameters: List[cx.Intent.Parameter],
        **kwargs,
    ) -> None:
        super().__init__(controller, training_phrases=training_phrases, **kwargs)
        self.parameters = parameters

    def get_intent(self):
        """Create and Intent object to be pushed to the API, including parameters."""
        return cx.Intent(
            {
                "display_name": self.display_name,
                "training_phrases": self.training_phrases,
                "parameters": self.parameters,
            }
        )
