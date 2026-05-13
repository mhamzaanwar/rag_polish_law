"""
Streamlit chat UI for the Polish Business Law RAG assistant.

Run: streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

# Make 'app' importable when run via streamlit
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from app.rag import get_pipeline

st.set_page_config(
    page_title="Polish Business Law RAG",
    page_icon="🇵🇱",
    layout="centered",
)

st.title("🇵🇱 Polish Business Law Assistant")
st.caption(
    "Ask about JDG registration, VAT thresholds, B2B contracting, and Polish tax basics. "
    "Every answer cites its source — no hallucinations."
)

# Initialise the pipeline once and cache it
@st.cache_resource(show_spinner="Loading vector index...")
def load_pipeline():
    return get_pipeline()

try:
    pipeline = load_pipeline()
except Exception as e:
    st.error(f"Failed to load RAG pipeline: {e}")
    st.info("Make sure you ran `python scripts/build_index.py` first.")
    st.stop()

# Sidebar — example questions and meta info
with st.sidebar:
    st.header("Try asking")
    examples = [
        "How do I register a JDG as a non-EU citizen?",
        "What's the VAT registration threshold in Poland?",
        "Can I do B2B contracting with a US company on JDG?",
        "What's the difference between JDG and Sp. z o.o.?",
        "Do I need an accountant for JDG?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.pending_question = ex

    st.divider()
    st.caption("Built by [Your Name] — backend dev specializing in production AI agents and RAG systems.")
    st.caption("[Hire me on Upwork](https://upwork.com/freelancers/yourprofile)")

# Chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"Sources ({len(msg['sources'])})"):
                for s in msg["sources"]:
                    st.markdown(f"**{s['name']}**")
                    st.text(s["preview"])

# Handle pending example button
question = st.session_state.pop("pending_question", None) or st.chat_input(
    "Ask a question about Polish business law..."
)

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Searching sources..."):
            response = pipeline.query(question)
        st.markdown(response.answer)

        with st.expander(f"Sources ({len(response.sources)}) · {response.latency_ms}ms"):
            for s in response.sources:
                st.markdown(f"**{s['name']}**")
                st.text(s["preview"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": response.answer,
            "sources": response.sources,
        })
