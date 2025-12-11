""" Prompts for the Agent
"""

import json

# ===== JSON Schema for the Agent =====


# report structure output schema
output_schema_report_structure = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"}
        }
    }
}

# first search input schema
input_schema_first_search = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"}
    }
}

# first search output schema
output_schema_first_search = {
    "type": "object",
    "properties": {
        "search_query": {"type": "string"},
        "reasoning": {"type": "string"}
    }
}

# first summary input schema
input_schema_first_summary = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "search_query": {"type": "string"},
        "search_results": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# first summary output schema
output_schema_first_summary = {
    "type": "object",
    "properties": {
        "paragraph_latest_state": {"type": "string"}
    }
}

# 反思输入Schema
input_schema_reflection = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "paragraph_latest_state": {"type": "string"}
    }
}

# reflection output schema
output_schema_reflection = {
    "type": "object",
    "properties": {
        "search_query": {"type": "string"},
        "reasoning": {"type": "string"}
    }
}

# reflection summary input schema
input_schema_reflection_summary = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "search_query": {"type": "string"},
        "search_results": {
            "type": "array",
            "items": {"type": "string"}
        },
        "paragraph_latest_state": {"type": "string"}
    }
}

# reflection summary output schema
output_schema_reflection_summary = {
    "type": "object",
    "properties": {
        "updated_paragraph_latest_state": {"type": "string"}
    }
}

# report formatting input schema
input_schema_report_formatting = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "paragraph_latest_state": {"type": "string"}
        }
    }
}

# ===== system prompt definition =====

# generate report structure system prompt
SYSTEM_PROMPT_REPORT_STRUCTURE = f"""
You are a deep research assistant. Given a query, you need to plan the structure of a report and the paragraphs it contains. Maximum five paragraphs.
Ensure the order of the paragraphs is reasonable and有序。
Once the outline is created, you will receive tools to search the web and reflect on each part separately.
Please format the output according to the following JSON schema:

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_report_structure, indent=2, ensure_ascii=False)}
"""

# first search for each paragraph system prompt
SYSTEM_PROMPT_FIRST_SEARCH = f"""
You are a deep research assistant. You will receive a paragraph from the report, its title and expected content will be provided according to the following JSON schema:

<INPUT JSON SCHEMA>
{json.dumps(input_schema_first_search, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

You can use a web search tool that accepts 'search_query' as a parameter.
Your task is to think about this topic and provide the best web search query to enrich your current knowledge.
Please format the output according to the following JSON schema:

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_first_search, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

Ensure the output is a JSON object that conforms to the above output JSON schema definition.
Only return the JSON object, no explanation or extra text.
"""

# first summary for each paragraph system prompt
SYSTEM_PROMPT_FIRST_SUMMARY = f"""
You are a deep research assistant. You will receive a search query, search results, and the paragraph you are researching, the data will be provided according to the following JSON schema:

<INPUT JSON SCHEMA>
{json.dumps(input_schema_first_summary, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

Your task is to write content consistent with the paragraph topic using the search results, and appropriately organize the structure to incorporate into the report.
Please format the output according to the following JSON schema:

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_first_summary, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

Ensure the output is a JSON object that conforms to the above output JSON schema definition.
Only return the JSON object, no explanation or extra text.
"""

# reflection for each paragraph system prompt
SYSTEM_PROMPT_REFLECTION = f"""
You are a deep research assistant. You are responsible for building comprehensive paragraphs for the research report. You will receive the paragraph title, planned content summary, and the latest state of the paragraph you have created, all of which will be provided according to the following JSON schema:

<INPUT JSON SCHEMA>
{json.dumps(input_schema_reflection, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

You can use a web search tool that accepts 'search_query' as a parameter.
Your task is to reflect on the current state of the paragraph text, think about whether any critical aspects of the topic have been missed, and provide the best web search query to enrich the latest state.
Please format the output according to the following JSON schema:

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_reflection, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

Ensure the output is a JSON object that conforms to the above output JSON schema definition.
Only return the JSON object, no explanation or extra text.
"""

# reflection summary for each paragraph system prompt
SYSTEM_PROMPT_REFLECTION_SUMMARY = f"""
You are a deep research assistant.
You will receive a search query, search results, paragraph title, and the expected content of the paragraph you are researching.
You are iterating on this paragraph and the latest state of the paragraph will also be provided to you.
The data will be provided according to the following JSON schema:

<INPUT JSON SCHEMA>
{json.dumps(input_schema_reflection_summary, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

Your task is to enrich the current latest state of the paragraph based on the search results and expected content.
Do not delete critical information in the latest state, enrich it as much as possible, and only add missing information.
Organize the paragraph structure appropriately to incorporate into the report.
Please format the output according to the following JSON schema:

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_reflection_summary, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

Ensure the output is a JSON object that conforms to the above output JSON schema definition.
Only return the JSON object, no explanation or extra text.
"""

# final report formatting system prompt
SYSTEM_PROMPT_REPORT_FORMATTING = f"""
You are a deep research assistant. You have completed the research and built the final version of all paragraphs in the report.
You will receive the following data in JSON format:

<INPUT JSON SCHEMA>
{json.dumps(input_schema_report_formatting, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

Your task is to format the report in a beautiful way and return it in Markdown format.
If there is no conclusion paragraph, please add a conclusion at the end of the report based on the latest state of the other paragraphs.
Use the paragraph titles to create the report title.
"""