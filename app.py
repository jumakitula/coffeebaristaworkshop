import time
from pathlib import Path
import streamlit as st

# Auto-seed database if missing on cold start
db_path = Path("coffebaristaagent/barista.db")
if not db_path.exists():
    from coffebaristaagent.init_hybrid_db import setup_databases
    setup_databases()

from coffebaristaagent.agent import create_barista_chat

st.set_page_config(page_title="AI Coffee Barista", page_icon="☕", layout="centered")

st.title("☕ AI Barista Assistant")
st.caption("Powered by Google Gemini & Hybrid RAG (SQLite + ChromaDB)")

if "chat" not in st.session_state:
    st.session_state.chat = create_barista_chat()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt
if prompt := st.chat_input("What would you like to order today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        def generate_response():
            # stream_tokens=True prints output as it arrives
            response_stream = st.session_state.chat.send_message_stream(prompt)
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        reply = st.write_stream(generate_response)
        st.session_state.messages.append({"role": "assistant", "content": reply})
