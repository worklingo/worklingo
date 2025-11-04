import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

# === CONFIG ===
load_dotenv()

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

HISTORY_FILE = "sprak_historik.json"

# Load history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# System prompt (dynamisk baserat på val)
def get_system_prompt(ui_lang, target_lang, branch, difficulty):
    branches = {
        "IT": "tekniska termer inom IT och programmering",
        "Medicin": "medicinska termer och vårdspråk",
        "Business": "affärs- och marknadsföringstermer",
        "Vardag": "vardagligt språk för konversationer",
        "Kreativt": "kreativt skrivande och litteratur",
        "Juridik": "juridiska termer och kontrakt"
    }
    diffs = {
        "Nybörjare": "enkla förklaringar med grundläggande tips",
        "Medel": "medelavancerade förklaringar med exempel",
        "Avancerad": "djupgående analys med nyanser"
    }
    branch_desc = branches.get(branch, "allmän svenska")
    diff_desc = diffs.get(difficulty, "grundläggande")

    return f"""
Du är en språklärare för {target_lang}. UI-språk: {ui_lang}.
Användaren väljer bransch: {branch_desc}.
Svårighetsgrad: {diff_desc}.
Rätta/översätt meningar från annat språk till {target_lang}.
1. Rätta stavfel, grammatik, stil.
2. Ge bättre naturlig version.
3. Förklara fel på UI-språket ({ui_lang}).
4. Håll tonen uppmuntrande, rolig.
Svara på UI-språket. Kort och tydligt.
"""

# UI-språk och målspråk
UI_LANGUAGES = {
    "English": "English",
    "Svenska": "Svenska",
    "Español": "Español",
    "Français": "Français",
    "Deutsch": "Deutsch",
    "Italiano": "Italiano",
    "Português": "Português",
    "Nederlands": "Nederlands",
    "Polski": "Polski"
}

TARGET_LANGUAGES = {
    "Svenska": "Svenska",
    "English": "English",
    "Español": "Español",
    "Français": "Français",
    "Deutsch": "Deutsch",
    "Italiano": "Italiano"
}

BRANCHES = {
    "Svenska": ["IT", "Medicin", "Business", "Vardag", "Kreativt", "Juridik"],
    "English": ["IT", "Medicine", "Business", "Everyday", "Creative", "Legal"],
    # Lägg till översättningar för andra språk om behövs
}

DIFFICULTIES = ["Nybörjare", "Medel", "Avancerad"]

# === STREAMLIT APP ===
st.set_page_config(page_title="Worklingo v3.0", page_icon="🌍", layout="wide")
st.title("🌍 **WORKLINGO v3.0**")
st.caption("AI-språklärare med Grok – rätta, översätt och förbättra!")

# Sidebar för val
st.sidebar.header("🛠️ Inställningar")
ui_lang = st.sidebar.selectbox("UI-språk", list(UI_LANGUAGES.keys()), index=1)  # Default Svenska
target_lang = st.sidebar.selectbox("Målspråk", list(TARGET_LANGUAGES.keys()), index=0)  # Default Svenska

# Bransch – beroende på målspråk
branches = BRANCHES.get(ui_lang, ["IT", "Medicin", "Business", "Vardag", "Kreativt", "Juridik"])
branch = st.sidebar.selectbox("Bransch", branches)

difficulty = st.sidebar.selectbox("Svårighetsgrad", DIFFICULTIES)

# Load history
if "history" not in st.session_state:
    st.session_state.history = load_history()
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": get_system_prompt(ui_lang, target_lang, branch, difficulty)}]

# Display chat
for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant"):
        st.write(turn["assistant"])

# Input
if prompt := st.chat_input(f"Skriv en mening på {target_lang} (eller annat språk)..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": f"Översätt/rätta till {target_lang} i {branch}-kontext: {prompt}"})
    st.session_state.history.append({"user": prompt, "assistant": ""})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Grok tänker..."):
            try:
                stream = client.chat.completions.create(
                    model="grok-beta",
                    messages=st.session_state.messages,
                    stream=True,
                    temperature=0.7
                )
                response = ""
                placeholder = st.empty()
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        response += content
                        placeholder.write(response)
                
                # Save
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.history[-1]["assistant"] = response
                save_history(st.session_state.history)

            except Exception as e:
                st.error(f"Fel: {e} – Kontrollera API-nyckel!")

# Sidebar controls
with st.sidebar:
    st.header("Kontroller")
    if st.button("Rensa historik"):
        st.session_state.history = []
        st.session_state.messages = [{"role": "system", "content": get_system_prompt(ui_lang, target_lang, branch, difficulty)}]
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.success("Historik rensad!")
        st.rerun()

    if st.button("Spara historik"):
        save_history(st.session_state.history)
        st.success(f"Sparad till {HISTORY_FILE}")

    st.divider()
    st.caption("Byggd med Grok API | v3.0 – Full version")
