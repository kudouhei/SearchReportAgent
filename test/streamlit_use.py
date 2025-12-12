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

def main():
    st.set_page_config(
        page_title =" Search Report Agent",
        page_icon = "🔍",
        layout = "wide",
    )
    st.title("Search Report Agent")
    st.markdown("A Deep Search Agent based on DeepSeek")


    # sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # API Keys Configuration
        st.subheader("API Keys")
        deepseek_key = st.text_input("DeepSeek API Key", type="password", value="")
        tavily_key = st.text_input("Tavily API Key", type="password", value="")
        
        st.subheader("Advanced Configuration")
        max_reflections = st.slider("Max Reflections", 1, 5, 2)
        max_search_results = st.slider("Max Search Results", 1, 10, 3)
        max_content_length = st.number_input("Max Content Length", 1000, 50000, 20000)
        
        # LLM Provider Selection
        llm_provider = st.selectbox("LLM Provider", ["deepseek", "openai"])
        
        # Initialize openai_key to avoid NameError
        openai_key = ""
        
        if llm_provider == "deepseek":
            model_name = st.selectbox("DeepSeek Model", ["deepseek-chat"])
        else:
            model_name = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o"])
            openai_key = st.text_input("OpenAI API Key", type="password", value="")

    # main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Research Query")
        query = st.text_area(
            "Enter the query you want to research",
            placeholder="For example: ...",
            height=100
        )

        # Preset Query Examples
        st.subheader("Example Queries")
        example_queries = [
            "The development trend of AI agents",

        ]

        selected_example = st.selectbox("Example Queries", ["Custom"] + example_queries)
        if selected_example != "Custom":
            query = selected_example

    with col2:
        st.header("Status Information")
        # Create empty containers for dynamic updates
        status_total = st.empty()
        status_completed = st.empty()
        status_progress = st.empty()
        status_info = st.empty()
        
        # Store containers in session state for access during execution
        st.session_state.status_containers = {
            'total': status_total,
            'completed': status_completed,
            'progress': status_progress,
            'info': status_info
        }
        
        # Update status display
        if 'agent' in st.session_state and hasattr(st.session_state.agent, 'state'):
            progress = st.session_state.agent.get_progress_summary()
            status_total.metric("Total Paragraphs", progress['total_paragraphs'])
            status_completed.metric("Completed", progress['completed_paragraphs'])
            status_progress.progress(progress['progress_percentage'] / 100)
            status_info.empty()
        else:
            status_total.empty()
            status_completed.empty()
            status_progress.empty()
            status_info.info("Not started yet")

    # Execute 
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        start_research = st.button("Start Research", type="primary", use_container_width=True)

    # Validate Configuration
    if start_research:
        if not query.strip():
            st.error("Please enter the research query")
            return
        
        if not deepseek_key and llm_provider == "deepseek":
            st.error("Please provide the DeepSeek API Key")
            return
        
        if not tavily_key:
            st.error("Please provide the Tavily API Key")
            return
        
        if llm_provider == "openai" and not openai_key:
            st.error("Please provide the OpenAI API Key")
            return
        
        # Create Agent
        # Create Configuration
        config = Config(
            deepseek_api_key=deepseek_key if llm_provider == "deepseek" else None,
            openai_api_key=openai_key if llm_provider == "openai" else None,
            tavily_api_key=tavily_key,
            default_llm_provider=llm_provider,
            deepseek_model=model_name if llm_provider == "deepseek" else "deepseek-chat",
            openai_model=model_name if llm_provider == "openai" else "gpt-4o-mini",
            max_reflections=max_reflections,
            max_search_results=max_search_results,
            max_content_length=max_content_length,
            output_dir="streamlit_reports"
        )

        # Execute Research
        execute_research(query, config)

def execute_research(query: str, config: Config):
    """Execute the research"""
    try:
        # Create Progress Bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Helper function to update status display
        def update_status_display():
            if 'agent' in st.session_state and hasattr(st.session_state.agent, 'state'):
                if 'status_containers' in st.session_state:
                    progress = st.session_state.agent.get_progress_summary()
                    st.session_state.status_containers['total'].metric("Total Paragraphs", progress['total_paragraphs'])
                    st.session_state.status_containers['completed'].metric("Completed", progress['completed_paragraphs'])
                    st.session_state.status_containers['progress'].progress(progress['progress_percentage'] / 100)
                    st.session_state.status_containers['info'].empty()
        
        # Initialize Agent
        status_text.text("Initializing Agent...")
        agent = SearchReportAgent(config)
        st.session_state.agent = agent
        update_status_display()
        
        progress_bar.progress(10)
        
        # Generate Report Structure
        status_text.text("Generating Report Structure...")
        agent._generate_report_structure(query)
        update_status_display()
        progress_bar.progress(20)
        
        # Process Paragraphs
        total_paragraphs = len(agent.state.paragraphs)
        for i in range(total_paragraphs):
            status_text.text(f"Processing Paragraph {i+1}/{total_paragraphs}: {agent.state.paragraphs[i].title}")
            
            # Initial Search and Summary
            agent._initial_search_and_summary(i)
            update_status_display()
            progress_value = 20 + (i + 0.5) / total_paragraphs * 60
            progress_bar.progress(int(progress_value))
            
            # Reflection Loop
            agent._reflection_loop(i)
            agent.state.paragraphs[i].research.mark_completed()
            update_status_display()
            
            progress_value = 20 + (i + 1) / total_paragraphs * 60
            progress_bar.progress(int(progress_value))
        
        # Generate Final Report
        status_text.text("Generating Final Report...")
        final_report = agent._generate_final_report()
        update_status_display()
        progress_bar.progress(90)
        
        # Save Report
        status_text.text("Saving Report...")
        agent._save_report(final_report)
        update_status_display()
        progress_bar.progress(100)
        
        status_text.text("Research completed!")
        
        # Display Results
        display_results(agent, final_report)
        
    except Exception as e:
        st.error(f"Error occurred during research: {str(e)}")

def display_results(agent: SearchReportAgent, final_report: str):
    """Display the research results"""
    st.header("Research Results")
    
    # Result Tabs
    tab1, tab2, tab3 = st.tabs(["Final Report", "Detailed Information", "Download"])
    
    with tab1:
        st.markdown(final_report)
    
    with tab2:
        # Paragraph Details
        st.subheader("Paragraph Details")
        for i, paragraph in enumerate(agent.state.paragraphs):
            with st.expander(f"Paragraph {i+1}: {paragraph.title}"):
                st.write("**Expected Content:**", paragraph.content)
                st.write("**Final Content:**", paragraph.research.latest_summary[:300] + "..." 
                        if len(paragraph.research.latest_summary) > 300 
                        else paragraph.research.latest_summary)
                st.write("**Search Count:**", paragraph.research.get_search_count())
                st.write("**Reflection Count:**", paragraph.research.reflection_iteration)
        
        # Search History
        st.subheader("Search History")
        all_searches = []
        for paragraph in agent.state.paragraphs:
            all_searches.extend(paragraph.research.search_history)
        
        if all_searches:
            for i, search in enumerate(all_searches):
                with st.expander(f"Search {i+1}: {search.query}"):
                    st.write("**URL:**", search.url)
                    st.write("**Title:**", search.title)
                    st.write("**Content Preview:**", search.content[:200] + "..." if len(search.content) > 200 else search.content)
                    if search.score:
                        st.write("**Relevance Score:**", search.score)
    
    with tab3:
        # Download Options
        st.subheader("Download Report")
        
        # Markdown Download
        st.download_button(
            label="Download Markdown Report",
            data=final_report,
            file_name=f"deep_search_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
        
        # JSON State Download
        state_json = agent.state.to_json()
        st.download_button(
            label="Download State File",
            data=state_json,
            file_name=f"deep_search_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()        