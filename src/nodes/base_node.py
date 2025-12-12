"""
Base node class
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..llms.base import BaseLLM
from ..state.state import State

class BaseNode(ABC):
    """
    Base node class
    """
    def __init__(self, llm_client: BaseLLM, node_name: str):
        self.llm_client = llm_client
        self.node_name = node_name or self.__class__.__name__

    @abstractmethod
    def run(self, input_data: Any, **kwargs) -> Any:
        """
        Run the node
        Args:
            input_data: the input data for the node
            **kwargs: additional arguments for the node
        Returns:
            the output data from the node
        """
        pass

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate the input data for the node
        Args:
            input_data: the input data for the node
        Returns:
            True if the input data is valid, False otherwise
        """
        return True

    def process_output(self, output: Any) -> Any:
        """
        Process the output data from the node
        Args:
            output_data: the output data from the node
        Returns:
            the processed output data
        """
        return output

    def log_info(self, message: str):
        """
        Log the information of the node
        Args:
            message: the message to log
        """
        print(f"[{self.node_name}] {message}")

    def log_error(self, message: str):
        """
        Log the error of the node
        Args:
            message: the message to log
        """
        print(f"[{self.node_name}] Error: {message}")

class StateMutationNode(BaseNode):
    """
    State mutation node class
    """
    @abstractmethod
    def mutate_state(self, input_data: Any, state: State, **kwargs) -> State:
        """
        Mutate the state
        Args:
            state: the state to mutate
        Returns:
            the mutated state
        """
        pass