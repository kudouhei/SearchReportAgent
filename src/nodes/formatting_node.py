"""
Formatting node class
"""

import json
from typing import List, Dict, Any

from .base_node import BaseNode
from ..prompts import SYSTEM_PROMPT_REPORT_FORMATTING
from ..utils.text_processing import (
    remove_reasoning_from_output,
    clean_markdown_tags
)

class ReportFormattingNode(BaseNode):
    """
    Formatting node class
    """
    def __init__(self, llm_client):
        super().__init__(llm_client, "ReportFormattingNode")

    def validate_input(self, input_data: Any) -> bool:
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                return isinstance(data, list) and all(
                    isinstance(item, dict) and "title" in item and "paragraph_latest_state" in item
                    for item in data
                )
            except:
                return False
        elif isinstance(input_data, list):
            return all(
                isinstance(item, dict) and "title" in item and "paragraph_latest_state" in item
                for item in input_data
            )
        else:
            return False
        
    def run(self, input_data: Any, **kwargs) -> str:
        try:
            if not self.validate_input(input_data):
                raise ValueError("Invalid input data")

            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info(f"Reporting Formatting...")

            # invoke the LLM
            response = self.llm_client.invoke(SYSTEM_PROMPT_REPORT_FORMATTING, message)

            # validate the response
            processed_response = self.process_output(response)
            self.log_info(f"Reporting Formatting completed")
            return processed_response
        except Exception as e:
            self.log_error(f"Failed to format the report: {e}")
            raise e

    def process_output(self, output: str) -> str:
        """
        Process the output from the LLM
        Args:
            output: the output from the LLM
        Returns:
            the processed output
        """
        try:
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_markdown_tags(cleaned_output)
            
            # validate the output
            if not cleaned_output.strip():
                raise ValueError("Empty output")

            if not cleaned_output.strip().startswith("#"):
                cleaned_output = f"# Search Report: {cleaned_output}"
            
            return cleaned_output.strip()
        except Exception as e:
            self.log_error(f"Failed to process the output: {e}")
            raise e
    
    def format_report_manually(self, paragraphs_data: List[Dict[str, str]], report_title: str="Search Report") -> str:
        """
        Format the report manually
        Args:
            paragraphs_data: the data of the paragraphs
            report_title: the title of the report
        Returns:
            the formatted report
        """
        try:
            self.log_info(f"Formatting report manually...")

            # format the report
            report_lines = [
                f"# {report_title}",
                "",
                "---",
                ""
            ]

            # add the paragraphs
            for i, paragraph in enumerate(paragraphs_data, 1):
                title = paragraph.get("title", f"Paragraph {i}")
                content = paragraph.get("paragraph_latest_state", "")

                if content:
                    report_lines.extend([
                        f"## {title}",
                        "",
                        content,
                        "",
                        "---",
                        ""
                    ])
            
            # add the conclusion
            if len(paragraphs_data) > 1:
                report_lines.extend([
                    f"# Conclusion",
                    "",
                    "---",
                    ""
                ])
            
            # join the report lines
            report = "\n".join(report_lines)
            self.log_info(f"Report formatted manually")
            return report
        except Exception as e:
            self.log_error(f"Failed to format the report manually: {e}")
            raise e