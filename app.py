cat << 'EOF' > app.py
import time
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Auto-seed database if running on Streamlit Cloud without pre-built db
db_path = Path("coffebaristaagent/barista.db")
if not db_path.exists():
    from coffebaristaagent.init_hybrid_db import setup_databases
    setup_databases()

from coffebaristaagent.agent import create_barista_chat

st.set_page_config(
    page_title="☕ Coffee Shop - Barista Bot",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Coffee Shop Header
st.markdown("""
<div class="header-container" style="text-align: center; padding: 24px; background: linear-gradient(135deg, #8B5E3C, #6F4E37); color: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px;">
    <h1 style="margin: 0; font-size: 2.4rem; font-weight: 700; color: white;">☕ Coffee Shop Barista Bot</h1>
    <p style="margin: 8px 0 0 0; font-size: 1.1rem; opacity: 0.95; color: #F5EBE6;">
        Powered by Google Gemini & Hybrid RAG (SQLite + ChromaDB)
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar with Menu Guide & Quick Filters
with st.sidebar:
    st.markdown("## ☕ Coffee Shop Menu")
    st.markdown("Explore our offerings and ask the barista for grounded recommendations.")
    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    st.markdown("- *'What iced drinks do you have under $4.50?'*")
    st.markdown("- *'I have a dairy allergy, what pastries can I get?'*")
    st.markdown("- *'Something warm with a cinnamon kick to wake me up'*")
    st.markdown("---")
    st.caption("Grounded strictly in SQLite & ChromaDB vector store.")

# Initialize chat session
if "chat" not in st.session_state:
    st.session_state.chat = create_barista_chat()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to ☕ Coffee Shop! What can I get started for you today?"}
    ]

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask for recommendations (e.g., 'What dairy-free pastries do you have?')"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Brewing your answer..."):
            reply = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = st.session_state.chat.send_message(prompt)
                    reply = response.text
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1.5)
                    else:
                        st.session_state.chat = create_barista_chat()
                        try:
                            response = st.session_state.chat.send_message(prompt)
                            reply = response.text
                        except Exception as final_e:
                            reply = f"Apologies, I ran into an error: {final_e}"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
EOF
