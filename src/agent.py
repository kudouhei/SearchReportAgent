"""
Search Agent main class
Integrate all modules, implement the complete deep search process
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from .llms import DeepSeekLLM, OpenAILLM, BaseLLM
from .nodes import (
    ReportStructureNode,
    FirstSearchNode, 
    ReflectionNode,
    FirstSummaryNode,
    ReflectionSummaryNode,
    ReportFormattingNode
)
from .state import State
from .tools import tavily_search
from .utils import Config, load_config, format_search_results_for_prompt

class SearchReportAgent:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        # initialize the LLM client
        self.llm_client = self._initialize_llm()

        # initialize the nodes
        self._initialize_nodes()
        
        # initialize the state
        self.state = State()
        
        # ensure the output directory exists
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        print(f"Search Report Agent initialized")
        print(f"Using LLM: {self.llm_client.get_model_info()}")

    def _initialize_llm(self) -> BaseLLM:
        """
        Initialize the LLM client
        """
        if self.config.default_llm_provider == "deepseek":
            return DeepSeekLLM(api_key=self.config.deepseek_api_key, model_name=self.config.deepseek_model)
        elif self.config.default_llm_provider == "openai":
            return OpenAILLM(api_key=self.config.openai_api_key, model_name=self.config.openai_model)
        else:
            raise ValueError(f"Invalid LLM provider: {self.config.default_llm_provider}")

    def _initialize_nodes(self):
        """
        Initialize the nodes
        """
        self.first_search_node = FirstSearchNode(llm_client=self.llm_client)
        self.reflection_node = ReflectionNode(llm_client=self.llm_client)
        self.first_summary_node = FirstSummaryNode(llm_client=self.llm_client)
        self.reflection_summary_node = ReflectionSummaryNode(llm_client=self.llm_client)
        self.report_formatting_node = ReportFormattingNode(llm_client=self.llm_client)

    def research(self, query: str, save_report: bool = True) -> str:
        """
        Research the query
        """
        print(f"\n{'='*60}")
        print(f"Starting the research report: {query}")
        print(f"{'='*60}")

        # generate the report structure
        try:
            # 1. Generate the report structure
            self._generate_report_structure(query)

            # 2. Process the paragraphs
            self._process_paragraphs()

            # 3. Generate the final report
            final_report = self._generate_final_report()

            # 4. Save the report
            if save_report:
                self._save_report(final_report)

            print(f"\n{'='*60}")
            print("Research report completed")
            print(f"{'='*60}")
            
            return final_report
        except Exception as e:
            print(f"Failed to research the query: {e}")
            raise e

    def _generate_report_structure(self, query: str):
        print(f"\n[Step] Generating the report structure...")
        
        # create the report structure node
        report_structure_node = ReportStructureNode(self.llm_client, query)
        
        # generate the structure and update the state
        self.state = report_structure_node.mutate_state(state=self.state)
        
        print(f"The report structure has been generated, with {len(self.state.paragraphs)} paragraphs:")
        for i, paragraph in enumerate(self.state.paragraphs, 1):
            print(f"  {i}. {paragraph.title}")

    def _process_paragraphs(self):
        print(f"\n[Step] Processing the paragraphs...")
        total_paragraphs = len(self.state.paragraphs)

        for i in range(total_paragraphs):
            print(f"\n[Paragraph {i + 1}/{total_paragraphs}] Processing...")
            # initial search and summary
            self._initial_search_and_summary(i)
            
            # reflection loop
            self._reflection_loop(i)
            
            # mark the paragraph as completed
            self.state.paragraphs[i].research.mark_completed()
            
            progress = (i + 1) / total_paragraphs * 100
            print(f"Paragraph {i + 1} processed ({progress:.1f}%)")

    def _initial_search_and_summary(self, paragraph_index: int):
        print(f"\n[Step] Initial search and summary for paragraph {paragraph_index + 1}...")
        paragraph = self.state.paragraphs[paragraph_index]
        
        search_input = {
            "title": paragraph.title,
            "content": paragraph.content,
        }

        # generate the search query
        print("  - Generating the search query...")
        search_output = self.first_search_node.run(search_input)
        search_query = search_output["search_query"]
        reasoning = search_output["reasoning"]

        print(f"  - Search query: {search_query}")
        print(f"  - Reasoning: {reasoning}")

        # perform the initial search
        print("  - Performing the initial search...")
        search_results = tavily_search(
            search_query,
            max_results=self.config.max_search_results,
            timeout=self.config.search_timeout,
            api_key=self.config.tavily_api_key
        )
        
        if search_results:
            print(f"  - Found {len(search_results)} search results")
            for j, result in enumerate(search_results, 1):
                print(f"    {j}. {result['title'][:50]}...")
        else:
            print("  - No search results found")

        # update search history
        paragraph.research.add_search_results(search_query, search_results)

        # generate the summary
        print("  - Generating the summary...")
        summary_input = {
            "title": paragraph.title,
            "content": paragraph.content,
            "search_query": search_query,
            "search_results": format_search_results_for_prompt(search_results, self.config.max_search_results),
        }
        
        # update the state
        self.state = self.first_summary_node.mutate_state(
            summary_input, self.state, paragraph_index
        )

        print(f"  - Summary: {self.state.paragraphs[paragraph_index].research.latest_summary}")
        
    def _reflection_loop(self, paragraph_index: int):
        print(f"\n[Step] Reflection loop for paragraph {paragraph_index + 1}...")
        paragraph = self.state.paragraphs[paragraph_index]
        
        # reflection loop
        for reflection_iteration in range(self.config.max_reflections):
            print(f"\n[Reflection {reflection_iteration + 1}/{self.config.max_reflections}] Iterating...")

            reflection_input = {
                "title": paragraph.title,
                "content": paragraph.content,
                "paragraph_latest_state": paragraph.research.latest_summary,
            }

            # generate the search query
            print("  - Generating the search query...")
            reflection_output = self.reflection_node.run(reflection_input)
            search_query = reflection_output["search_query"]
            reasoning = reflection_output["reasoning"]

            print(f"  - Search query: {search_query}")
            print(f"  - Reasoning: {reasoning}") 

            # perform the search
            print("  - Performing the search...")
            search_results = tavily_search(
                search_query,
                max_results=self.config.max_search_results,
                timeout=self.config.search_timeout,
                api_key=self.config.tavily_api_key
            )

            if search_results:
                print(f"  - Found {len(search_results)} search results")

            # update search history
            paragraph.research.add_search_results(search_query, search_results)
            
            # generate the summary
            print("  - Generating the summary...")
            reflection_summary_input = {
                "title": paragraph.title,
                "content": paragraph.content,
                "search_query": search_query,
                "search_results": format_search_results_for_prompt(search_results, self.config.max_content_length),
                "paragraph_latest_state": paragraph.research.latest_summary,
            }
            
            # update the state
            self.state = self.reflection_summary_node.mutate_state(
                reflection_summary_input, self.state, paragraph_index
            )

            print(f"  - Summary: {self.state.paragraphs[paragraph_index].research.latest_summary}")
            
           
    def _generate_final_report(self) -> str:
        print(f"\n[Step] Generating the final report...")
        
        report_data = []
        for paragraph in self.state.paragraphs:
            report_data.append({
                "title": paragraph.title,
                "paragraph_latest_state": paragraph.research.latest_summary
            })

        try:
            final_report = self.report_formatting_node.run(report_data)
            print(f"  - Final report: {final_report}")
        except Exception as e:
            print(f"Failed to generate the final report: {e}")
            raise e

        # update the state
        self.state.final_report = final_report
        self.state.mark_completed()

        print(f"  - Final report: {final_report}")
        return final_report

    def _save_report(self, report: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = "".join(c for c in self.state.query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        query_safe = query_safe.replace(' ', '_')[:30]
        
        filename = f"deep_search_report_{query_safe}_{timestamp}.md"
        filepath = os.path.join(self.config.output_dir, filename)

        # save the report
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"  - Report saved to {filepath}")

        # save the state (if configured)
        if self.config.save_intermediate_states:
            state_filename = f"state_{query_safe}_{timestamp}.json"
            state_filepath = os.path.join(self.config.output_dir, state_filename)
            self.state.save_to_file(state_filepath)
            print(f"The state has been saved to {state_filepath}")

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get the progress summary"""
        return self.state.get_progress_summary()
    
    def load_state(self, filepath: str):
        """Load the state from a file"""
        self.state = State.load_from_file(filepath)
        print(f"The state has been loaded from {filepath}")
    
    def save_state(self, filepath: str):
        """Save the state to a file"""
        self.state.save_to_file(filepath)
        print(f"The state has been saved to {filepath}")

def create_agent(config_file: Optional[str] = None) -> SearchReportAgent:
    """
    Convenient function to create a Deep Search Agent instance
    
    Args:
        config_file: The path to the configuration file
        
    Returns:
        SearchReportAgent instance
    """
    config = load_config(config_file)
    return SearchReportAgent(config)