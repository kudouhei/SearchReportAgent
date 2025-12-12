"""
Search Report Agent
A Search Report Agent implementation without any framework
"""

from .agent import SearchReportAgent, create_agent
from .utils.config import Config, load_config

__version__ = "1.0.0"
__author__ = "Search Report Agent Team"

__all__ = ["SearchReportAgent", "create_agent", "Config", "load_config"]