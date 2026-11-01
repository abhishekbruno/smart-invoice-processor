import sys
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from config.settings import settings
from core.database import db
from core.gemini_service import gemini_service
from core.rag_pipeline import RAGResponse, rag_pipeline
from core.vector_store import vector_store
from utils.helpers import format_financial_markdown

st.set_page_config(page_title="Ask AI | Smart Invoice Processor", layout="wide")

st.title("Ask AI Document Intelligence")
st.caption("Natural-language invoice question answering powered by Hybrid SQL + ChromaDB RAG + Google Gemini API.")

# System Diagnostics Bar
gemini_health = gemini_service.check_health()
v_stats = vector_store.get_stats()

status_c1, status_c2, status_c3 = st.columns([1.5, 1.5, 1])

with status_c1:
    if gemini_health.get("is_available"):
        active_model = gemini_health.get("active_model") or gemini_health.get("configured_model")
        st.success(f"**Google Gemini Online** (`{active_model}`)")
    else:
        st.warning("**Gemini Offline / Unconfigured** (Deterministic SQL & structured retrieval active)")

with status_c2:
    st.info(f"**Vector Store:** {v_stats.get('total_chunks', 0)} chunks ({v_stats.get('unique_invoices_indexed', 0)} invoices)")

with status_c3:
    if st.button("Clear Chat", key="clear_chat_btn", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not gemini_health.get("is_available"):
    with st.expander("Gemini API Connection Information"):
        st.warning(gemini_health.get("error", "GEMINI_API_KEY is missing or invalid."))
        st.caption("To enable Gemini API, ensure `GEMINI_API_KEY` is set in your `.env` file.")

st.markdown("---")

# Suggested Example Questions
st.markdown("##### Example Queries (Click to Ask):")
example_queries = [
    "What is our total spending in INR?",
    "How much did we spend on AWS in INR?",
    "Convert our Microsoft invoice to rupees.",
    "Compare Google Cloud and AWS expenses in Indian Rupees.",
    "What was the INR equivalent of our January 2024 AWS invoice?",
    "Which invoices contain cloud storage charges?",
]

example_cols = st.columns(3)
selected_example = None
for i, ex in enumerate(example_queries):
    with example_cols[i % 3]:
        if st.button(ex, key=f"ex_btn_{i}", use_container_width=True):
            selected_example = ex

# Chat Session State Initialization
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am your Smart Invoice Assistant powered by Google Gemini API, Relational SQL, and Multi-Currency Conversion.\n\n"
                "• **Exact Math:** Ask about total expenses, comparisons, dates, or vendor spend (executed via verified SQLite SQL).\n"
                "• **Currency Conversion:** Ask for spending converted into Indian Rupees (INR) or other currencies using daily European Central Bank rates.\n"
                "• **Document Insights:** Ask about specific services, line items, contract terms, or invoice summaries (grounded with ChromaDB + Gemini)."
            ),
            "query_type": "system",
            "is_llm": False,
            "sources": [],
        }
    ]

# Display Conversation History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        q_type = msg.get("query_type")
        is_llm = msg.get("is_llm", False)

        if q_type == "sql":
            st.markdown("`🟢 [Deterministic SQL - 100% Mathematical Precision]`")
        elif q_type == "rag":
            if is_llm:
                st.markdown("`🟣 [AI-Generated RAG - Google Gemini API]`")
            else:
                st.markdown("`🟠 [Structured Vector Retrieval - Gemini Offline]`")
        elif q_type == "hybrid":
            if is_llm:
                st.markdown("`🔵 [Hybrid SQL Calculations + Gemini Document Explanation]`")
            else:
                st.markdown("`🔵 [Hybrid SQL Calculations + Document Snippets]`")

        st.markdown(format_financial_markdown(msg["content"]))

        sources = msg.get("sources", [])
        if sources:
            with st.expander(f"📑 Supporting Sources & Evidence ({len(sources)} citations)", expanded=False):
                for s in sources:
                    fn = s.get("filename", "invoice.pdf")
                    inv_no = s.get("invoice_number", "")
                    inv_str = f" | Invoice #{inv_no}" if inv_no and inv_no != "N/A" else ""
                    pg = s.get("page_number", 1)
                    snippet = s.get("snippet", "")
                    sim = s.get("similarity", 0.0)

                    sim_badge = f" [Score: {sim:.2f}]" if sim > 0 else ""
                    st.markdown(f"**📄 `{fn}`{inv_str} (Page {pg}){sim_badge}**")
                    if snippet:
                        st.caption(f"> \"{snippet}\"")
                    st.markdown("---")

# Handle Input
user_prompt = st.chat_input("Ask a question about your invoices...")
if selected_example:
    user_prompt = selected_example

if user_prompt:
    # 1. Add user message
    st.session_state.messages.append(
        {"role": "user", "content": user_prompt, "query_type": "user", "is_llm": False, "sources": []}
    )
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Run through RAG Pipeline
    with st.chat_message("assistant"):
        with st.spinner("Analyzing query, retrieving records, and synthesizing answer with Gemini..."):
            response: RAGResponse = rag_pipeline.answer_query(user_prompt)

            # Display badge
            if response.query_type == "sql":
                st.markdown("`🟢 [Deterministic SQL - 100% Mathematical Precision]`")
            elif response.query_type == "rag":
                if response.is_llm_generated:
                    st.markdown("`🟣 [AI-Generated RAG - Google Gemini API]`")
                else:
                    st.markdown("`🟠 [Structured Vector Retrieval - Gemini Offline]`")
            elif response.query_type == "hybrid":
                if response.is_llm_generated:
                    st.markdown("`🔵 [Hybrid SQL Calculations + Gemini Document Explanation]`")
                else:
                    st.markdown("`🔵 [Hybrid SQL Calculations + Document Snippets]`")

            formatted_answer = format_financial_markdown(response.answer)
            st.markdown(formatted_answer)

            # Display Citations
            if response.sources:
                with st.expander(f"📑 Supporting Sources & Evidence ({len(response.sources)} citations)", expanded=False):
                    for s in response.sources:
                        s_dict = s.to_dict()
                        fn = s_dict.get("filename", "invoice.pdf")
                        inv_no = s_dict.get("invoice_number", "")
                        inv_str = f" | Invoice #{inv_no}" if inv_no and inv_no != "N/A" else ""
                        pg = s_dict.get("page_number", 1)
                        snippet = s_dict.get("snippet", "")
                        sim = s_dict.get("similarity", 0.0)

                        sim_badge = f" [Score: {sim:.2f}]" if sim > 0 else ""
                        st.markdown(f"**📄 `{fn}`{inv_str} (Page {pg}){sim_badge}**")
                        if snippet:
                            st.caption(f"> \"{snippet}\"")
                        st.markdown("---")

    # 3. Save assistant message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": formatted_answer,
            "query_type": response.query_type,
            "is_llm": response.is_llm_generated,
            "sources": [s.to_dict() for s in response.sources],
        }
    )
