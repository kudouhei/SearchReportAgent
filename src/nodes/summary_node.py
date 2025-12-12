"""
Summary node implementation
Responsible for generating and updating the paragraph content based on the search results
"""

import json
from typing import Any
from json.decoder import JSONDecodeError

from .base_node import StateMutationNode
from ..state.state import State
from ..prompts import SYSTEM_PROMPT_FIRST_SUMMARY, SYSTEM_PROMPT_REFLECTION_SUMMARY
from ..utils.text_processing import (
    remove_reasoning_from_output,
    clean_json_tags,
)

class FirstSummaryNode(StateMutationNode):
    """Node for generating the first summary of the paragraph based on the search results"""
    
    def __init__(self, llm_client):
        super().__init__(llm_client, "FirstSummaryNode")
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate the input data"""
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                required_fields = ["title", "content", "search_query", "search_results"]
                return all(field in data for field in required_fields)
            except JSONDecodeError:
                return False
        elif isinstance(input_data, dict):
            required_fields = ["title", "content", "search_query", "search_results"]
            return all(field in input_data for field in required_fields)
        return False
    
    def run(self, input_data: Any, **kwargs) -> str:
        """
        Invoke the LLM to generate the paragraph summary
        """
        try:
            if not self.validate_input(input_data):
                raise ValueError("Invalid input data, it should contain title, content, search_query and search_results fields")
            
            # prepare the input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Generating the first paragraph summary")
            
            # invoke the LLM
            response = self.llm_client.invoke(SYSTEM_PROMPT_FIRST_SUMMARY, message)
            
            # process the response
            processed_response = self.process_output(response)
            
            self.log_info("First paragraph summary generated")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate the first paragraph summary: {e}")
            raise e
    
    def process_output(self, output: str) -> str:
        """
        Process the LLM output, extract the paragraph summary
        """
        try:
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            try:
                result = json.loads(cleaned_output)
            except JSONDecodeError:
                # if not JSON format, return the cleaned output
                return cleaned_output
            
            # extract the paragraph content
            if isinstance(result, dict):
                paragraph_content = result.get("paragraph_latest_state", "")
                if paragraph_content:
                    return paragraph_content
            
            # if extraction fails, return the original cleaned output
            return cleaned_output
            
        except Exception as e:
            self.log_error(f"Failed to process the output: {e}")
            return "Failed to generate the paragraph summary"
    
    def mutate_state(self, input_data: Any, state: State, paragraph_index: int, **kwargs) -> State:
        """
        Update the latest summary of the paragraph to the state
        Args:
            input_data: the input data
            state: the current state
            paragraph_index: the index of the paragraph
            **kwargs: additional arguments
        Returns:
            the updated state
        """
        try:
            # generate the summary
            summary = self.run(input_data, **kwargs)
            
            # update the state
            if 0 <= paragraph_index < len(state.paragraphs):
                state.paragraphs[paragraph_index].research.latest_summary = summary
                self.log_info(f"Updated the first summary of the paragraph {paragraph_index}")
            else:
                raise ValueError(f"Paragraph index {paragraph_index} out of range")
            
            state.update_timestamp()
            return state
            
        except Exception as e:
            self.log_error(f"Failed to update the state: {e}")
            raise e

class ReflectionSummaryNode(StateMutationNode):
    """Node for updating the paragraph summary based on the reflection search results"""
    
    def __init__(self, llm_client):
        """
        Initialize the reflection summary node
        """
        super().__init__(llm_client, "ReflectionSummaryNode")
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate the input data"""
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                required_fields = ["title", "content", "search_query", "search_results", "paragraph_latest_state"]

                return all(field in data for field in required_fields)
            except JSONDecodeError:
                return False
        elif isinstance(input_data, dict):
            required_fields = ["title", "content", "search_query", "search_results", "paragraph_latest_state"]
            return all(field in input_data for field in required_fields)
        return False
    
    def run(self, input_data: Any, **kwargs) -> str:
        """
        Invoke the LLM to update the paragraph content
        """
        try:
            if not self.validate_input(input_data):
                raise ValueError("Invalid input data, it should contain title, content, search_query, search_results and paragraph_latest_state fields")
            
            # prepare the input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Generating the reflection summary")
            
            # invoke the LLM
            response = self.llm_client.invoke(SYSTEM_PROMPT_REFLECTION_SUMMARY, message)
            
            # process the response
            processed_response = self.process_output(response)
            
            self.log_info("Reflection summary generated")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate the reflection summary: {e}")
            raise e
    
    def process_output(self, output: str) -> str:
        """
        Process the LLM output, extract the updated paragraph content
        """
        try:
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            try:
                result = json.loads(cleaned_output)
            except JSONDecodeError:
                return cleaned_output
            
            if isinstance(result, dict):
                updated_content = result.get("updated_paragraph_latest_state", "")
                if updated_content:
                    return updated_content
            
            return cleaned_output
            
        except Exception as e:
            self.log_error(f"Failed to process the output: {e}")
            return "Failed to generate the reflection summary"
    
    def mutate_state(self, input_data: Any, state: State, paragraph_index: int, **kwargs) -> State:
        """
        Update the latest summary of the paragraph to the state
        """
        try:
            # 生成更新后的总结
            updated_summary = self.run(input_data, **kwargs)
            
            # 更新状态
            if 0 <= paragraph_index < len(state.paragraphs):
                state.paragraphs[paragraph_index].research.latest_summary = updated_summary
                state.paragraphs[paragraph_index].research.increment_reflection_iteration()
                self.log_info(f"Updated the reflection summary of the paragraph {paragraph_index}")
            else:
                raise ValueError(f"Paragraph index {paragraph_index} out of range")
            
            state.update_timestamp()
            return state
            
        except Exception as e:
            self.log_error(f"Failed to update the state: {e}")
            raise e