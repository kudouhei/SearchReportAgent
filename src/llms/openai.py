"""
OpenAI LLM
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from .base import BaseLLM

class OpenAILLM(BaseLLM):
    """
    OpenAI LLM
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key is not set")

        super().__init__(api_key, model_name)

        self.client = OpenAI(api_key=api_key)

        self.default_model = model_name or self.get_default_model()

    def get_default_model(self) -> str:
        return "gpt-4o-mini"

    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Invoke the OpenAI LLM
        """
        try:
            messages = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}]

            params = {
                'model': self.default_model,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 4096),
            }

            response = self.client.chat.completions.create(**params)

            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return self.validata_response(content)
            else:
                return ""
        except Exception as e:
            raise ValueError(f"Failed to invoke OpenAI LLM: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get the information of the OpenAI model
        Returns:
            the information of the OpenAI model
        """
        return {
            'provider': 'OpenAI',
            "model": self.default_model,
            "api_base": "https://api.openai.com"
        }