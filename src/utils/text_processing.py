"""
Text Processing module
Clean LLM output, parse JSON, etc. for the Deep Search Agent
"""

import re
import json
from typing import Dict, Any, List
from json.decoder import JSONDecodeError

def clean_json_tags(text: str) -> str:
    """
    Clean the JSON tags from the text
    Args:text: the original text
    Returns: the cleaned text
    """
    # remove ```json and ``` tags
    text = re.sub(r'```json\s*', '', text)  # remove ```json and any whitespace after it
    text = re.sub(r'```\s*$', '', text)  # remove ``` and any whitespace before it
    text = re.sub(r'```', '', text)  # remove ```
    
    return text.strip()

def clean_markdown_tags(text: str) -> str:
    """
    Clean the Markdown tags from the text
    Args: text: the original text
    Returns: the cleaned text
    """
    # remove ``` and ``` tags
    text = re.sub(r'```markdown\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    text = re.sub(r'```', '', text)
    
    return text.strip()

def remove_reasoning_from_output(text: str) -> str:
    """
    Remove the reasoning from the text
    Args: text: the original text
    Returns: the text without reasoning
    """
    # remove the reasoning from the text
    patterns = [
        r'(?:reasoning| thinking| analyzing)[:]\s*.*?(?=\{|\[)',  # remove reasoning part
        r'(?:explanation| explanation| explanation of)[:]\s*.*?(?=\{|\[)',   # remove explanation part
        r'^.*?(?=\{|\[)',  # remove all text before JSON
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text.strip()

def extract_clean_response(text: str) -> Dict[str, Any]:
    """
    Extract the clean response from the text
    Args: text: the original text
    Returns: the clean response
    """
    # extract the clean response from the text
    cleaned_text = clean_json_tags(text)
    cleaned_text = remove_reasoning_from_output(cleaned_text)

    try:
        return json.loads(cleaned_text)
    except JSONDecodeError:
        pass

    # try to find the JSON object
    json_pattern = r'\{.*\}'
    match = re.search(json_pattern, cleaned_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except JSONDecodeError:
            pass
    
    # try to find the JSON array
    array_pattern = r'\[.*\]'
    match = re.search(array_pattern, cleaned_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except JSONDecodeError:
            pass

    print(f"Failed to parse JSON response: {cleaned_text[:200]}...")
    return {"error": "Failed to parse JSON response", "raw_text": cleaned_text}

def update_state_with_search_results(search_results: List[Dict[str, Any]], 
                                   paragraph_index: int, state: Any) -> Any:
    """
    Update the state with the search results
    Args: search_results: the search results
    Returns: the updated state
    """
    if 0 <= paragraph_index < len(state.paragraphs):
        # get the last search query (assume it is the current query)
        current_query = ""
        if search_results:
            # infer the query from the search results (here we need to improve to get the actual query)
            current_query = "search query"
        
        # add the search results to the state
        state.paragraphs[paragraph_index].research.add_search_results(
            current_query, search_results
        )
    
    return state

def validate_json_schema(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate if the JSON data contains the required fields
    Args:
        data: the data to validate
        required_fields: the required fields list
    Returns:
        True if the validation is passed, False otherwise
    """
    return all(field in data for field in required_fields)

def truncate_content(content: str, max_length: int = 20000) -> str:
    """
    Truncate the content to the specified length
    Args:
        content: the original content
        max_length: the maximum length
    Returns:
        the truncated content
    """
    if len(content) <= max_length:
        return content
    
    # try to truncate at the word boundary
    truncated = content[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # if the last space position is reasonable
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."

def format_search_results_for_prompt(search_results: List[Dict[str, Any]], 
                                   max_length: int = 20000) -> List[str]:
    """
    Format the search results for the prompt
    Args: search_results: the search results
    Returns: the formatted search results
    """
    return [truncate_content(result.get('content', ''), max_length) for result in search_results]