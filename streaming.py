from anthropic.types import MessageParam

from message import add_user_message, client, model

messages: list[MessageParam] = []
add_user_message(messages, "Write a 1 sentence description of a fake database")

with client.messages.stream(
    model=model,
    max_tokens=1000,
    messages=messages,
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
