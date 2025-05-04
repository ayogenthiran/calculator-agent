import openai
import json
from typing import List, Dict, Any, Optional, Union, Literal

from src.llm.llm_base import LLMClientBase


class MessageHistory:
    def __init__(self, messages: Optional[List[Any]] = None) -> None:
        self.messages = messages or []

    def add_system_message(self, content: str) -> None:
        self.messages.append({"role": "system", "content": content})

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_result_message(self, result: Union[int, float], tool_call_id: str) -> None:
        self.messages.append({
            "role": "tool",
            "content": json.dumps({"result": result}),
            "tool_call_id": tool_call_id
        })

    def add_generic_message(self, msg: Any) -> None:
        self.messages.append(msg)

    def get_messages(self):
        return self.messages

    # def __str__(self):
    #     return str(self.messages)

    def __repr__(self) -> str:
        return str(self.messages)


class ChatGPTError(Exception):
    """Base class for ChatGPT client errors."""
    pass


class ChatGPTClient(LLMClientBase):
    def __init__(self, config: dict):
        self.client = openai.OpenAI(api_key=config['api_key'])

        self.model: str = config['model']
        self.tool_definitions: List[Dict] = config['tool_definitions']
        self.tool_call_required: Literal['none', 'auto', 'required'] = config['tool_call_required']

    def run_prompt(self, msg_history: MessageHistory) -> Any:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=msg_history.get_messages(),
                tools=self.tool_definitions,
                tool_choice=self.tool_call_required,
            )
        except openai.OpenAIError as e:
            raise ChatGPTError(f"API error: {str(e)}") from e
        except Exception as e:
            raise ChatGPTError(f"Unexpected error: {str(e)}") from e

        response = completion.choices[0].message
        return response
