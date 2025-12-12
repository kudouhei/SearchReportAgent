"""
Streamlit Web interface
Provide a friendly Web interface for the Deep Search Agent
"""

import os
import sys
import streamlit as st
from datetime import datetime
import json

# add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SearchReportAgent, Config

