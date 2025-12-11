"""
Base class for LLMs
define the interface for the LLMs
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseLLM(ABC):
    """
    Base class for LLMs
    """
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Invoke the LLM, return the response from the LLM
        Args:
            system_prompt: the system prompt for the LLM
            user_prompt: the user prompt for the LLM
            **kwargs: additional arguments for the LLM
        Returns:
            the response from the LLM
        """
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """
        Get the default model for the LLM
        Returns:
            the default model for the LLM
        """
        pass

    def validata_response(self, response: str) -> str:
        """
        Validate the response from the LLM
        Args:
            response: the original response from the LLM
        Returns:
            the processed response from the LLM
        """
        if response is None:
            return ""
        return response.strip()

