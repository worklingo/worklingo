import streamlit as st
import openai
from gtts import gTTS
import random

st.set_page_config(page_title="Worklingo v3.1", layout="wide")

# ENKEL INLOGGNING – INGEN AUTH-BIBLIOTEK
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("### Logga in")
    username = st.text_input("Användarnamn", value="user")
    password = st.text_input("Lösenord", type="password", value="pass")
    if st.button("Logga in"):
        if username == "user" and password == "pass":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Fel användarnamn eller lösenord")
    st.stop()

if st.button("Logga ut", key="logout"):
    st.session_state.logged_in = False
    st.rerun()

# TEMA
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

# SESSION
for key in ["historik", "poang", "niva", "current_exercise"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "historik" else 0 if key == "poang" else "Nybörjare" if key == "niva" else None

st.markdown("<h1 style='text-align:center; color:#006400;'>Worklingo v3.1</h1>", unsafe_allow_html=True)
st.markdown(f"**Poäng: <span style='color:green;font-weight:bold'>{st.session_state.poang}</span>** | **Nivå: {st.session_state.niva}**", unsafe_allow_html=True)

ui_sprak = ["Русский", "Polski", "English"]
mal_sprak = ["Svenska", "English"]
mal_codes = {"Svenska
