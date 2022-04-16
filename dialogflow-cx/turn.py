from google.cloud.dialogflowcx import (
    ConversationTurn,
    QueryInput,
    ResponseMessage,
    TextInput,
)


class Turn:
    def __init__(
        self, user_input, agent_output, page_delegator, triggered_intent_delegator=None
    ):

        self.user_input = user_input
        self.triggered_intent_delegator = triggered_intent_delegator
        self.page_delegator = page_delegator
        self.agent_output = agent_output

    def get_conversation_turn(self, is_webhook_enabled):
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
