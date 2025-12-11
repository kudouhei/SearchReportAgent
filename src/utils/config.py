"""
Config module
Define the configuration for the Deep Search Agent
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class Config:
    """
    Config class
    """
    # api keys
    deepseek_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None

    # model configuration
    default_llm_provider: str = "deepseek"  
    deepseek_model: str = "deepseek-chat"
    openai_model: str = "gpt-4o-mini"

    # search configuration
    max_search_results: int = 3
    search_timeout: int = 200
    max_content_length: int = 20000

    # Agent configuration
    max_reflections: int = 2
    max_paragraphs: int = 6

    # output configuration
    output_dir: str = "reports"
    save_intermediate_states: bool = True

    def validate(self) -> bool:
        """
        Validate the configuration
        """
        if self.default_llm_provider == "deepseek" and not self.deepseek_api_key:
            print("Error: DeepSeek API Key is not set")
            return False
        
        if self.default_llm_provider == "openai" and not self.openai_api_key:
            print("Error: OpenAI API Key is not set")
            return False
        
        if not self.tavily_api_key:
            print("Error: Tavily API Key is not set")
            return False
        
        return True

    @classmethod
    def from_file(cls, config_file: str) -> 'Config':
        """
        Create a Config from a file
        """
        if config_file.endswith('.py'):
            import importlib.util

            spec = importlib.util.spec_from_file_location("config", config_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return cls(
                deepseek_api_key=getattr(module, "DEEPSEEK_API_KEY", None),
                openai_api_key=getattr(module, "OPENAI_API_KEY", None),
                tavily_api_key=getattr(module, "TAVILY_API_KEY", None),
                default_llm_provider=getattr(module, "DEFAULT_LLM_PROVIDER", "deepseek"),
                deepseek_model=getattr(module, "DEEPSEEK_MODEL", "deepseek-chat"),
                openai_model=getattr(module, "OPENAI_MODEL", "gpt-4o-mini"),
                max_search_results=getattr(module, "SEARCH_RESULTS_PER_QUERY", 3),
                search_timeout=getattr(module, "SEARCH_TIMEOUT", 200),
                max_content_length=getattr(module, "SEARCH_CONTENT_MAX_LENGTH", 20000),
                max_reflections=getattr(module, "MAX_REFLECTIONS", 2),
                max_paragraphs=getattr(module, "MAX_PARAGRAPHS", 6),
                output_dir=getattr(module, "OUTPUT_DIR", "reports"),
                save_intermediate_states=getattr(module, "SAVE_INTERMEDIATE_STATES", True)
            )
        else:
            # .env file
            config_dict = {}

            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            config_dict[key.strip()] = value.strip()
            
            return cls(**config_dict)

def load_config(config_file: Optional[str] = None) -> Config:
    """
    Load the configuration
    """
    if config_file:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
        file_to_load = config_file
    else:
        # try to load common config files
        for config_path in ["config.py", "config.env", ".env"]:
            if os.path.exists(config_path):
                file_to_load = config_path
                print(f"Found config file: {config_path}")
                break
        else:
            raise FileNotFoundError("Config file not found, please create config.py file")
            
    config = Config.from_file(file_to_load)

    if not config.validate():
        raise ValueError("Invalid configuration")

    return config

def print_config(config: Config):
    """
    Print the configuration
    """
    """Print the configuration (hide sensitive information)"""
    print("\n=== 当前配置 ===")
    print(f"LLM Provider: {config.default_llm_provider}")
    print(f"DeepSeek Model: {config.deepseek_model}")
    print(f"OpenAI Model: {config.openai_model}")
    print(f"Max Search Results: {config.max_search_results}")
    print(f"Search Timeout: {config.search_timeout} seconds")
    print(f"Max Content Length: {config.max_content_length}")
    print(f"Max Reflections: {config.max_reflections}")
    print(f"Max Paragraphs: {config.max_paragraphs}")
    print(f"Output Dir: {config.output_dir}")
    print(f"Save Intermediate States: {config.save_intermediate_states}")
        
    print(f"DeepSeek API Key: {'Set' if config.deepseek_api_key else 'Not Set'}")
    print(f"OpenAI API Key: {'Set' if config.openai_api_key else 'Not Set'}")
    print(f"Tavily API Key: {'Set' if config.tavily_api_key else 'Not Set'}")
    print("==================\n")