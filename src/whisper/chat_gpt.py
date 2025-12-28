from typing import Union, Optional, cast
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletion
)

class ChatGPT:

    def __init__(self, model: str, token: str, options: Optional[dict[str, str]]=None):
        if options is None:
            options = {}
        self.model: str = model
        self.token: str = token
        self.options: dict[str, str] = options if options is not None else {}
        self.client = OpenAI(api_key=token, **self.options)

    @staticmethod
    def list_to_chat_messages(messages: list[dict[str, str]]) -> list[
        Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam]]:
        result: list[Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam]] = []
        message: dict[str, str]
        for message in messages:
            if message["role"] == "system":
                result.append(ChatCompletionSystemMessageParam(role="system", content=message["content"]))
            elif message["role"] == "assistant":
                result.append(ChatCompletionAssistantMessageParam(role="assistant", content=message["content"]))
            elif message["role"] == "user":
                result.append(ChatCompletionUserMessageParam(role="user", content=message["content"]))
            else:
                raise ValueError(f"Invalid role: {message['role']}")
        return result

    def call(self, messages: list[dict[str, str]]) -> str:
        response: ChatCompletion = self.client.chat.completions.create(
            model=self.model,
            messages=ChatGPT.list_to_chat_messages(messages)
        )
        if response is None:
            raise RuntimeError("ChatGPT response is None")
        return cast(str, response.choices[0].message.content)

