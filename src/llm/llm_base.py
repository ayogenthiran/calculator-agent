from abc import ABC, abstractmethod


class LLMClientBase(ABC):
    @abstractmethod
    def run_prompt(self, msg_history):
        """Abstract method that should be implemented by child classes to run a prompt."""
        pass
