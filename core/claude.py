from anthropic import Anthropic, Omit, omit
from anthropic.types import (
    Message,
    MessageParam,
    ThinkingConfigParam,
    ToolParam,
    ToolResultBlockParam,
)

UserContent = str | Message | list[ToolResultBlockParam]


class Claude:
    def __init__(self, model: str) -> None:
        self.client = Anthropic()
        self.model = model

    def add_user_message(
        self, messages: list[MessageParam], message: UserContent
    ) -> None:
        user_message: MessageParam = {
            "role": "user",
            "content": message.content if isinstance(message, Message) else message,
        }
        messages.append(user_message)

    def add_assistant_message(
        self, messages: list[MessageParam], message: str | Message
    ) -> None:
        assistant_message: MessageParam = {
            "role": "assistant",
            "content": message.content if isinstance(message, Message) else message,
        }
        messages.append(assistant_message)

    def text_from_message(self, message: Message) -> str:
        return "\n".join(
            [block.text for block in message.content if block.type == "text"]
        )

    def chat(
        self,
        messages: list[MessageParam],
        system: str | Omit = omit,
        stop_sequences: list[str] | Omit = omit,
        tools: list[ToolParam] | Omit = omit,
        thinking: bool = False,
        thinking_budget: int = 1024,
    ) -> Message:
        thinking_config: ThinkingConfigParam | Omit = (
            {"type": "enabled", "budget_tokens": thinking_budget} if thinking else omit
        )

        return self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=messages,
            system=system,
            stop_sequences=stop_sequences,
            tools=tools,
            thinking=thinking_config,
        )
