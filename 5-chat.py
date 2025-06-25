import streamlit as st
import lancedb
from utils.db import connect_lancedb
from openai import OpenAI
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
import os

# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client
client = OpenAI()


# Initialize LanceDB connection
@st.cache_resource
def init_db_and_func():
    """Initialize database connection and embedding function."""
    db = connect_lancedb()
    func = get_registry().get("openai").create(name="text-embedding-3-large")
    table = db.open_table("docling")
    return table, func


def get_context(query: str, table, func, num_results: int = 5) -> str:
    """Search the database for relevant context and format it for citation.

    Args:
        query: User's question
        table: LanceDB table object
        func: Embedding function
        num_results: Number of results to return

    Returns:
        str: A formatted string of documents with sources for the LLM.
    """
    query_vector = func.generate_embeddings([query])[0]
    results = table.search(query_vector).limit(num_results).to_pandas()
    
    contexts = []
    for i, row in results.iterrows():
        metadata = row.get('metadata', {})
        report_reference = metadata.get('filename', 'Unknown Report')
        section_title = metadata.get('title')
        page_numbers = metadata.get('page_numbers', [])

        # Clean up the report reference for better display
        if report_reference != 'Unknown Report':
            report_reference = os.path.splitext(report_reference)[0].replace('-', ' ').replace('_', ' ')

        source_parts = [report_reference]
        if section_title:
            source_parts.append(section_title)
        
        if len(page_numbers) > 0:
            page_numbers_str = f"Page(s): {', '.join(map(str, page_numbers))}"
            source_parts.append(page_numbers_str)

        source_identifier = ", ".join(source_parts)

        context_str = f"Source: {source_identifier}\n"
        context_str += f"Content: {row['text']}"
        contexts.append(context_str)

    return "\n\n---\n\n".join(contexts)


def get_llm_response(prompt: str, context: str, system_prompt: str = "") -> str:
    """Get streaming response from OpenAI API.

    Args:
        prompt: User's question
        context: Retrieved context from database
        system_prompt: System prompt for the LLM

    Returns:
        str: Model's response
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": f"{context}\n\nQuestion: {prompt}"})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
    )

    return response


# Initialize Streamlit app
st.title("📚 USG Chatbot")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize database connection
table, func = init_db_and_func()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the document"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get relevant context
    with st.status("Searching document...", expanded=False) as status:
        context = get_context(prompt, table, func)
        st.markdown(
            """
            <style>
            .st-emotion-cache-1c7y2kd {
                flex-direction: row-reverse;
                text-align: right;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        status.update(label="Getting response...", state="running", expanded=False)

        # Get LLM response
        system_prompt = (
            "You are a helpful assistant. Answer the user's question based on the context provided below. "
            "The context is a list of documents, each with a 'Source' and 'Content' field. The 'Source' provides the report, section title, and page number. "
            "For each piece of information you use, you MUST cite the full source from which it came (e.g., 'According to 23 2026 CJ AMS, Federal Seed Program, Page(s): 1, ...')."
        )
        response = get_llm_response(prompt, context, system_prompt=system_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response.choices[0].message.content)
