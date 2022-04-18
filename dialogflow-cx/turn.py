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

"""Module for Turn class."""

import dataclasses
from typing import Optional

import intent_delegator as idy
import page_delegator as pd
from google.cloud.dialogflowcx import (
    ConversationTurn,
    QueryInput,
    ResponseMessage,
    TextInput,
)


@dataclasses.dataclass(frozen=True)
class Turn:
    """Turn class reorganizes a conversational turn using Dialogflow CX protos."""

    user_input: str
    agent_output: str
    page_delegator: pd.PageDelegator
    triggered_intent_delegator: Optional[idy.IntentDelegator] = None

    def get_conversation_turn(self, is_webhook_enabled):
        """Gets a ConversationTurn object from user input and the expected response."""
        text_responses = [ResponseMessage.Text(text=text) for text in self.agent_output]
        if not self.triggered_intent_delegator:
            triggered_intent = None
        else:
            triggered_intent = self.triggered_intent_delegator.intent
        virtual_agent_output = ConversationTurn.VirtualAgentOutput(
            current_page=self.page_delegator.page,
            triggered_intent=triggered_intent,
            text_responses=text_responses,
        )
        return ConversationTurn(
            virtual_agent_output=virtual_agent_output,
            user_input=ConversationTurn.UserInput(
                is_webhook_enabled=is_webhook_enabled,
                input=QueryInput(
                    text=TextInput(
                        text=self.user_input,
                    )
                ),
            ),
        )
