"""
Search node implementation
Responsible for generating search queries and reflection queries
"""

import json
from typing import Dict, Any
from json.decoder import JSONDecodeError

from .base_node import BaseNode
from ..prompts import SYSTEM_PROMPT_FIRST_SEARCH, SYSTEM_PROMPT_REFLECTION
from ..utils.text_processing import (
    remove_reasoning_from_output,
    clean_json_tags,
    extract_clean_response
)

class FirstSearchNode(BaseNode):
    """Generate the first search query for the paragraph"""
    
    def __init__(self, llm_client):
        super().__init__(llm_client, "FirstSearchNode")
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate the input data"""
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                return "title" in data and "content" in data
            except JSONDecodeError:
                return False

        elif isinstance(input_data, dict):
            return "title" in input_data and "content" in input_data
        return False
    
    def run(self, input_data: Any, **kwargs) -> Dict[str, str]:
        """
        Invoke the LLM to generate the search query and reasoning
        Args:
            input_data: the input data containing title and content
            **kwargs: additional arguments
        Returns:
            the dictionary containing search_query and reasoning
        """
        try:
            if not self.validate_input(input_data):
                raise ValueError("Invalid input data, it should contain title and content fields")
            
            # prepare the input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Generating the first search query")
            
            # invoke the LLM
            response = self.llm_client.invoke(SYSTEM_PROMPT_FIRST_SEARCH, message)
            
            # process the response
            processed_response = self.process_output(response)
            
            self.log_info(f"First search query generated: {processed_response.get('search_query', 'N/A')}")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate the first search query: {e}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, str]:
        """
        Process the LLM output, extract the search query and reasoning
        Args:
            output: the original output from the LLM
        Returns:
            the dictionary containing search_query and reasoning
        """
        try:
            # clean the response text
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            # parse the JSON
            try:
                result = json.loads(cleaned_output)
            except JSONDecodeError:
                # use a more powerful extraction method
                result = extract_clean_response(cleaned_output)
                if "error" in result:
                    raise ValueError("JSON解析失败")
            
            # validate and clean the result
            search_query = result.get("search_query", "")
            reasoning = result.get("reasoning", "")
            
            if not search_query:
                raise ValueError("Search query not found")
            
            return {
                "search_query": search_query,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.log_error(f"Failed to process the output: {e}")
            # return the default query
            return {
                "search_query": "Research on the related topic",
                "reasoning": "Due to parsing failure, using the default search query"
            }

class ReflectionNode(BaseNode):
    """Reflect on the paragraph and generate a new search query"""
    
    def __init__(self, llm_client):
        """
        Initialize the reflection node
        Args:
            llm_client: LLM client
        """
        super().__init__(llm_client, "ReflectionNode")
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate the input data"""
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                required_fields = ["title", "content", "paragraph_latest_state"]
                return all(field in data for field in required_fields)
            except JSONDecodeError:
                return False
        elif isinstance(input_data, dict):
            required_fields = ["title", "content", "paragraph_latest_state"]
            return all(field in input_data for field in required_fields)
        return False
    
    def run(self, input_data: Any, **kwargs) -> Dict[str, str]:
        """
        Invoke the LLM to reflect and generate a new search query
        
        Args:
            input_data: the input data containing title, content and paragraph_latest_state
            **kwargs: additional arguments
        Returns:
            the dictionary containing search_query and reasoning
        """
        try:
            if not self.validate_input(input_data):
                raise ValueError("Invalid input data, it should contain title, content and paragraph_latest_state fields")
            
            # prepare the input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Reflecting and generating a new search query")
            
            # invoke the LLM
            response = self.llm_client.invoke(SYSTEM_PROMPT_REFLECTION, message)
            
            # process the response
            processed_response = self.process_output(response)
            
            self.log_info(f"Reflection search query generated: {processed_response.get('search_query', 'N/A')}")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate the reflection search query: {e}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, str]:
        """
        Process the LLM output, extract the search query and reasoning
        Args:
            output: the original output from the LLM
        Returns:
            the dictionary containing search_query and reasoning
        """
        try:
            # clean the response text
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            # parse the JSON
            try:
                result = json.loads(cleaned_output)
            except JSONDecodeError:
                # use a more powerful extraction method
                result = extract_clean_response(cleaned_output)
                if "error" in result:
                    raise ValueError("Failed to parse the JSON")
            
            # validate and clean the result
            search_query = result.get("search_query", "")
            reasoning = result.get("reasoning", "")
            
            if not search_query:
                raise ValueError("Search query not found")
            
            return {
                "search_query": search_query,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.log_error(f"Failed to process the output: {e}")
            return {
                "search_query": "Research on the related topic",
                "reasoning": "Due to parsing failure, using the default reflection search query"
            }