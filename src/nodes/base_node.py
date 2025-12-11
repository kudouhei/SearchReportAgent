"""
Base node class
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseNode(ABC):
    """
    Base node class
    """
    def __init__(self, name: str):
        self.name = name
        