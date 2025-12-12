"""
DeepSeek LLM
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from .base import BaseLLM

class DeepSeekLLM(BaseLLM):
    """
    DeepSeek LLM
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize the DeepSeek client
        
        Args:
            api_key: DeepSeek API key, if not provided, read from environment variable
            model_name: model name, default is deepseek-chat
        """
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DeepSeek API key is not set")

        super().__init__(api_key, model_name)

        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        self.default_model = model_name or self.get_default_model()

    def get_default_model(self) -> str:
        """
        Get the default model for the DeepSeek LLM
        """
        return "deepseek-chat"

    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Invoke the DeepSeek LLM
        a
        Args:
            system_prompt: the system prompt for the DeepSeek LLM
            user_prompt: the user prompt for the DeepSeek LLM
            **kwargs: parameters, such as temperature, max_tokens, etc.
        Returns:
            the response from the DeepSeek LLM
        """
        try:
            messages = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}]

            params = {
                'model': self.default_model,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 4096),
                'stream': kwargs.get('stream', False),
            }

            response = self.client.chat.completions.create(**params)

            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return self.validate_response(content)
            else:
                return ""
        except Exception as e:
            raise ValueError(f"Failed to invoke DeepSeek LLM: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get the information of the DeepSeek model
        Returns:
            the information of the DeepSeek model
        """
        return {
            'provider': 'DeepSeek',
            "model": self.default_model,
            "api_base": "https://api.deepseek.com"
        }
        