import streamlit as st
import openai
import json
from gtts import gTTS
import streamlit_authenticator as stauth
import stripe
from pathlib import Path
import random

st.set_page_config(page_title="Worklingo v3.1", layout="wide")
stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    .main {background: #f0f8f0;}
    .stApp {font-family: 'Roboto', sans-serif;}
    [data-testid="stHeader"] {background: #006400;}
    [data-testid="stHeader"] h1 {color: white !important;}
    .stTextInput > div > div > input {border: 2px solid #90EE90; border-radius: 12px; padding: 10px;}
    .stButton > button {background: #006400; color: white; border-radius: 20px; border: none; padding: 10px 24px; font-weight: bold;}
    .stButton > button:hover {background: #90EE90; color: black;}
    .chat-user {background: #90EE90; color: black; border-radius: 15px; padding: 12px; margin: 5px 0; max-width: 80%;}
    .chat-bot {background: #006400; color: white; border-radius: 15px; padding: 12px; margin: 5px 0; max-width: 80%;}
    .exercise-box {border: 2px solid #90EE90; border-radius: 12px; padding: 15px; margin: 10px 0; background: #fafffa;}
</style>
""", unsafe_allow_html=True)

users_file = Path("users.json")
if not users_file.exists():
    default = {"credentials": {"usernames": {}}, "cookie": {"expiry_days": 30, "key": "worklingo_signature_key_2025", "name": "worklingo_auth"}, "preauthorized": []}
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(default, f, ensure_ascii=False, indent=2)

authenticator = stauth.Authenticate(users_file, "worklingo_auth", "worklingo_signature_key_2025", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Logga in", "main")

if not authentication_status:
    st.error("Logga in med **user / pass**")
    st.stop()
authenticator.logout("Logga ut", "sidebar")

for key in ["historik", "poang", "niva", "current_exercise"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "historik" else 0 if key == "poang" else "Nybörjare" if key == "niva" else None

st.markdown("<h1 style='text-align:center; color:#006400;'>Worklingo v3.1</h1>", unsafe_allow_html=True)
col_p, col_s = st.columns([2,1])
with col_p:
    st.markdown(f"**{name}** | **Poäng: <span style='color:green;font-weight:bold'>{st.session_state.poang}</span>** | **Nivå: {st.session_state.niva}**", unsafe_allow_html=True)
with col_s:
    if st.button("9€/mån Premium"):
        st.markdown("[**Betala nu (test)**](https://buy.stripe.com/test_abc123)", unsafe_allow_html=True)

ui_sprak = ["Українська", "Русский", "Polski", "Slovenčina", "Српски", "Б
