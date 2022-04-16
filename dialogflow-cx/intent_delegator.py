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

    _CLIENT_CLASS = IntentsClient

    def __init__(self, controller: ds.DialogflowSample, **kwargs) -> None:
        super().__init__(controller, **kwargs)

    @property
    def intent(self):
        if not self._intent:
            raise RuntimeError("Intent not yet created")
        return self._intent

    def initialize(self, training_phrases_text):
        # Create an intent-triggered transition into the page:

        training_phrases = []
        for training_phrase_text in training_phrases_text:
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
