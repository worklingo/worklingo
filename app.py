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
mal_codes = {"Svenska": "sv", "English": "en"}
branscher = ["Sjukvård (hemtjänst)", "Bygg", "Restaurang"]

c1, c2, c3 = st.columns(3)
with c1: ui_val = st.selectbox("Ditt språk", ui_sprak, key="ui")
with c2: mal_val = st.selectbox("Lär dig", mal_sprak, key="mal")
with c3: bransch_val = st.selectbox("Bransch", branscher, key="bransch")

tab_chatt, tab_ovning = st.tabs(["Jobbchatt", "Övningar"])

with tab_chatt:
    prompt_text = f"Skriv på **{ui_val}** om ditt jobb – jag rättar till **{mal_val}**"
    user_input = st.chat_input(prompt_text)

    if user_input:
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)

        client = openai.OpenAI(base_url="https://api.x.ai/v1", api_key=st.secrets["XAI_API_KEY"])
        system_prompt = f"Rätta meningen till perfekt {mal_val} för {bransch_val}. Svara: 1. Korrekt mening 2. Poäng: X/10 3. Förklaring"
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
        )
        bot_reply = response.choices[0].message.content.strip()

        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-bot">{bot_reply}</div>', unsafe_allow_html=True)

        poang = 5
        if "Poäng" in bot_reply:
            try:
                poang = int([s for s in bot_reply.split() if s.isdigit()][0])
            except: pass
        st.session_state.poang += poang
        if st.session_state.poang > 150: st.session_state.niva = "Proffs"
        elif st.session_state.poang > 50: st.session_state.niva = "Medveten"

        correct_sentence = bot_reply.split('\n')[0].strip()
        if st.button("Hör uttal", key=f"tts_{len(st.session_state.historik)}"):
            tts = gTTS(correct_sentence, lang=mal_codes[mal_val])
            tts.save("uttal.mp3")
            st.audio("uttal.mp3")

        st.session_state.historik.append({"user": user_input, "bot": bot_reply})

with tab_ovning:
    st.header("Övningar")
    if st.button("Ny övning"):
        st.session_state.current_exercise = {"q": "Fyll i: 'Jag ______ patienten.'", "a": ["hjälper"], "type": "fill"}
        st.rerun()

    if st.session_state.current_exercise:
        ex = st.session_state.current_exercise
        ans = st.text_input("Svar", key="ex_ans")
        if st.button("Kontrollera"):
            if ans.lower() == ex["a"][0].lower():
                st.success("Rätt! +10 poäng")
                st.session_state.poang += 10
            else:
                st.error(f"Fel. Rätt: {ex['a'][0]}")

with st.expander("Historik"):
    for h in st.session_state.historik[-5:]:
        st.write(f"**Du:** {h['user']}")
        st.write(f"**Bot:** {h['bot']}")
        st.divider()

st.success("KLART! Appen funkar – enkel inloggning!")
