import streamlit as st
import openai
import json
import os
from gtts import gTTS
import streamlit_authenticator as stauth
import stripe
from pathlib import Path
import random

# === CONFIG ===
st.set_page_config(page_title="Worklingo v3.1", layout="wide")
stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "")

# === GRÖN TEMA ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    .main {background: #f0f8f0;}
    .stApp {font-family: 'Roboto', sans-serif;}
    [data-testid="stHeader"] {background: #006400;}
    [data-testid="stHeader"] h1 {color: white !important;}
    .stTextInput > div > div > input {border: 2px solid #90EE90; border-radius: 12px; padding: 10px;}
    .stButton > button {
        background: #006400; color: white; border-radius: 20px; border: none;
        padding: 10px 24px; font-weight: bold;
    }
    .stButton > button:hover {background: #90EE90; color: black;}
    .chat-user {background: #90EE90; color: black; border-radius: 15px; padding: 12px; margin: 5px 0; max-width: 80%;}
    .chat-bot {background: #006400; color: white; border-radius: 15px; padding: 12px; margin: 5px 0; max-width: 80%;}
    .exercise-box {border: 2
