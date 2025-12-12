"""
Report structure generation node
Responsible for generating the overall structure of the report based on the query
"""

import json
from typing import Dict, Any, List
from json.decoder import JSONDecodeError

from .base_node import StateMutationNode
from ..state.state import State
from ..prompts import SYSTEM_PROMPT_REPORT_STRUCTURE
from ..utils.text_processing import (
    remove_reasoning_from_output,
    clean_json_tags,
    extract_clean_response
)

class ReportStructureNode(StateMutationNode):
    """
    Report structure generation node
    """
    def __init__(self, llm_client, query: str):
        """
        Initialize the report structure generation node
        Args:
            llm_client: LLM client
            query: user query
        """
        super().__init__(llm_client, "ReportStructureNode")
        self.query = query

    def validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, str) and len(self.query.strip()) > 0

    def run(self, input_data: Any, **kwargs) -> List[Dict[str, str]]:
        try:
            self.log_info(f"Generating report structure for query: {self.query}")
            
            # invoke the LLM
            response = self.llm_client.invoke(SYSTEM_PROMPT_REPORT_STRUCTURE, self.query)
            
            # validate the response
            processed_response = self.process_output(response)
            self.log_info(f"Report structure generated")
            return processed_response
        except Exception as e:
            self.log_error(f"Failed to generate the report structure: {e}")
            raise e

    def process_output(self, output: str) -> List[Dict[str, str]]:
        """
        Process the output from the LLM
        Args:
            output: the output from the LLM
        Returns:
            the processed output
        """
        try:
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            try:
                report_structure = json.loads(cleaned_output)
            except JSONDecodeError:
                report_structure = extract_clean_response(cleaned_output)

                if "error" in report_structure:
                    raise ValueError(report_structure["error"])

            if not isinstance(report_structure, list):
                raise ValueError("Invalid report structure")

            # validate the report structure
            validated_structure = []
            for i, paragraph in enumerate(report_structure):
                if not isinstance(paragraph, dict):
                    continue

                title = paragraph.get("title", f"Paragraph {i + 1}")
                content = paragraph.get("content", "")

                validated_structure.append({
                    "title": title.strip(),
                    "content": content.strip()
                })

            return validated_structure
        except Exception as e:
            self.log_error(f"Failed to process the output: {e}")
            return [
                {
                    "title": "Overview",
                    "content": f"The overall overview and background introduction of '{self.query}'"
                },
                {
                    "title": "Detailed Analysis", 
                    "content": f"Deep analysis of the related content of '{self.query}'"
                }
            ]

    def mutate_state(self, input_data: Any = None, state: State = None, **kwargs) -> State:
        """
        Write the report structure to the state
        Args:
            input_data: the input data
            state: the current state, if None then create a new state
            **kwargs: additional arguments
        """
        if state is None:
            state = State()
        
        try:
            # generate the report structure
            report_structure = self.run(input_data, **kwargs)
            
            # set the query and report title
            state.query = self.query
            if not state.report_title:
                state.report_title = f"Research Report of '{self.query}'"
            
            # add the paragraphs to the state
            for paragraph_data in report_structure:
                state.add_paragraph(
                    title=paragraph_data["title"],
                    content=paragraph_data["content"]
                )
            
            self.log_info(f"Added {len(report_structure)} paragraphs to the state")
            return state
            
        except Exception as e:
            self.log_error(f"Failed to update the state: {e}")
            raise e