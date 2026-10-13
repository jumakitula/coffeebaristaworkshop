import time
from pathlib import Path
import streamlit as st
from google.genai.errors import ServerError, APIError

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
        with st.spinner("Brewing a response..."):
            reply = None
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    response = st.session_state.chat.send_message(prompt)
                    reply = response.text
                    break
                except (ServerError, APIError) as e:
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))  # Exponential backoff (2s, 4s)
                    else:
                        # Re-instantiate chat session to reset state
                        try:
                            st.session_state.chat = create_barista_chat()
                            response = st.session_state.chat.send_message(prompt)
                            reply = response.text
                        except Exception as final_e:
                            reply = "Sorry, our barista system is experiencing high traffic right now. Please try your request once more in a few seconds!"
                except Exception as e:
                    reply = f"Error: {e}"
                    break

            # Stream words smoothly to the UI
            def text_streamer(text):
                for word in text.split(" "):
                    yield word + " "
                    time.sleep(0.02)

            rendered = st.write_stream(text_streamer(reply))
            st.session_state.messages.append({"role": "assistant", "content": reply})
