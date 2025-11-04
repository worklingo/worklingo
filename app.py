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

# Load/save history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# System prompt – JOBBA I BRANSCHEN
def get_system_prompt(ui_lang, target_lang, branch):
    branches = {
        "sjukvård": "jobba inom hemtjänst, som undersköterska eller vårdbiträde",
        "bygg": "jobba inom bygg och konstruktion",
        "restaurang": "jobba i restaurang och matlagning",
        "lager-logistik": "jobba i lager och logistik",
        "produktion": "jobba i produktion och tillverkning",
        "retail": "jobba i butik, affär och försäljning"
    }
    branch_desc = branches.get(branch.lower(), "allmänt arbete")

    return f"""
Du är en språklärare för {target_lang}. UI-språk: {ui_lang}.
Användaren arbetar inom {branch_desc}.
Rätta/översätt arbetsrelaterade meningar till {target_lang}.
1. Rätta stavfel, grammatik, fackspråk.
2. Ge bättre, naturlig version för arbetsplatsen.
3. Förklara på UI-språket ({ui_lang}).
4. Håll tonen uppmuntrande, professionell.
Svara på UI-språket. Kort och tydligt.
"""

# UI-språk
UI_LANGUAGES = {
    "Українська": "ukrainska",
    "Русский": "ryska",
    "Polski": "polska",
    "Slovenčina": "slovakiska",
    "Српски": "serbiska",
    "Български": "bulgariska",
    "Română": "rumänska",
    "Lietuvių": "litauiska",
    "English": "engelska"
}

# Målspråk
TARGET_LANGUAGES = {
    "Svenska": "svenska",
    "Norsk": "norska",
    "Dansk": "danska",
    "Deutsch": "tyska",
    "English": "engelska",
    "Nederlands": "holländska",
    "Español": "spanska",
    "Français": "franska",
    "Italiano": "italienska"
}

# Branscher
BRANCHES = ["Sjukvård", "Bygg", "Restaurang", "Lager-logistik", "Produktion", "Retail"]

# === APP ===
st.set_page_config(page_title="Worklingo v3.0", page_icon="🏗️", layout="wide")
st.title("🏗️ **WORKLINGO v3.0**")
st.caption("AI-språklärare för arbetslivet – med Grok")

# Sidebar
st.sidebar.header("⚙️ Inställningar")
ui_lang_key = st.sidebar.selectbox("UI-språk", list(UI_LANGUAGES.keys()))
ui_lang = UI_LANGUAGES[ui_lang_key]

target_lang_key = st.sidebar.selectbox("Målspråk", list(TARGET_LANGUAGES.keys()))
target_lang = TARGET_LANGUAGES[target_lang_key]

branch = st.sidebar.selectbox("Bransch", BRANCHES)

# Session state
if "history" not in st.session_state:
    st.session_state.history = load_history()
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": get_system_prompt(ui_lang, target_lang, branch)}]

# Chat
for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant"):
        st.write(turn["assistant"])

# Input
if prompt := st.chat_input(f"Skriv en arbetsrelaterad mening på {target_lang}..."):
    st.session_state.messages.append({"role": "user", "content": f"Rätta/översätt till {target_lang} inom {branch}: {prompt}"})
    st.session_state.history.append({"user": prompt, "assistant": ""})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Grok rättar..."):
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
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.history[-1]["assistant"] = response
                save_history(st.session_state.history)

            except Exception as e:
                st.error(f"Fel: {e}")

# Kontroller
with st.sidebar:
    st.header("Kontroller")
    if st.button("Rensa historik"):
        st.session_state.history = []
        st.session_state.messages = [{"role": "system", "content": get_system_prompt(ui_lang, target_lang, branch)}]
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.success("Rensat!")
        st.rerun()

    if st.button("Spara historik"):
        save_history(st.session_state.history)
        st.success("Sparat!")
