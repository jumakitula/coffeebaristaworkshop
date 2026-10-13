import time
import streamlit as st
from google.genai.errors import ServerError
from coffebaristaagent.agent import create_barista_chat

st.set_page_config(page_title="AI Coffee Barista", page_icon="☕")

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
                except ServerError as e:
                    if attempt < max_retries - 1:
                        time.sleep(1.5)  # Brief pause before retrying transient spike
                    else:
                        # Reset chat session to trigger fallback model
                        st.session_state.chat = create_barista_chat()
                        response = st.session_state.chat.send_message(prompt)
                        reply = response.text
                except Exception as e:
                    reply = f"Sorry, I encountered an error: {e}"
                    break

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
