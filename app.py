import streamlit as st
import json
import os
from dotenv import load_dotenv

# Load .env configurations before importing anything else
load_dotenv()


st.set_page_config(
    page_title="☕ Coffee Shop - Barista Bot",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<div class="header-container" style="text-align: center; padding: 20px; background: linear-gradient(135deg, #8B5E3C, #6F4E37); color: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; color: white;">☕ ☕ Coffee Shop</h1>
    <p style="margin: 5px 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">Your friendly AI Barista is ready to help you find the perfect drink or pastry!</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ☕ Coffee Shop Menu")
    st.markdown("Explore our offerings and ask the barista for recommendations.")
    st.markdown("---")


if "raw_history" not in st.session_state:
    st.session_state.raw_history = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to ☕ Coffee Shop! What can I get started for you today?"}
    ]

if prompt := st.chat_input("Ask for recommendations (e.g., 'What dairy-free pastries do you have?')"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Brewing your answer..."):
            try:
                from coffebaristaagent.agent import run_barista_agent
                response_text, updated_history = run_barista_agent(
                    prompt, 
                    history=st.session_state.raw_history
                )
                st.session_state.raw_history = updated_history
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Apologies, I ran into an error: {e}")  
