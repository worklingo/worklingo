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

ui_sprak = ["Українська", "Русский", "Polski", "Slovenčina", "Српски", "Български", "Română", "Lietuvių", "English"]
mal_sprak = ["Svenska", "Norsk", "Dansk", "Deutsch", "English", "Nederlands", "Español", "Français", "Italiano"]
mal_codes = {"Svenska": "sv", "Norsk": "no", "Dansk": "da", "Deutsch": "de", "English": "en", "Nederlands": "nl", "Español": "es", "Français": "fr", "Italiano": "it"}
branscher = ["Sjukvård (hemtjänst)", "Bygg", "Restaurang", "Lager-logistik", "Produktion", "Retail"]

c1, c2, c3 = st.columns(3)
with c1: ui_val = st.selectbox("Ditt språk", ui_sprak, key="ui")
with c2: mal_val = st.selectbox("Lär dig", mal_sprak, key="mal")
with c3: bransch_val = st.selectbox("Bransch", branscher, key="bransch")

tab_chatt, tab_ovning = st.tabs(["Jobbchatt", "Övningar"])

with tab_chatt:
    prompt_text = f"Skriv på **{ui_val}** om ditt jobb i **{bransch_val}** – jag rättar till **{mal_val}**"
    user_input = st.chat_input(prompt_text)

    if user_input:
        with st.chat_message("user", avatar="user"):
            st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)

        client = openai.OpenAI(base_url="https://api.x.ai/v1", api_key=st.secrets["XAI_API_KEY"])
        system_prompt = f"""
        Användaren arbetar inom {bransch_val}.
        Rätta/översätt meningen från {ui_val} till perfekt {mal_val}.
        Svara EXAKT:
        1. Korrekt mening på {mal_val}
        2. Poäng: X/10
        3. Förklaring: [kort]
        BARA JOBBRELATERAT!
        """
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
        )
        bot_reply = response.choices[0].message.content.strip()

        with st.chat_message("assistant", avatar="robot"):
            st.markdown(f'<div class="chat-bot">{bot_reply}</div>', unsafe_allow_html=True)

        poang_line = [line for line in bot_reply.split('\n') if "Poäng" in line]
        if poang_line:
            try:
                poang = int(poang_line[0].split('/')[0].split()[-1])
                st.session_state.poang += poang
            except:
                st.session_state.poang += 5
        else:
            st.session_state.poang += 5

        if st.session_state.poang > 150: st.session_state.niva = "Proffs"
        elif st.session_state.poang > 50: st.session_state.niva = "Medveten"

        correct_sentence = bot_reply.split('\n')[0].strip()
        if st.button("Hör uttal", key=f"tts_{len(st.session_state.historik)}"):
            tts = gTTS(correct_sentence, lang=mal_codes[mal_val])
            path = f"temp_{len(st.session_state.historik)}.mp3"
            tts.save(path)
            st.audio(path)

        st.session_state.historik.append({"user": user_input, "bot": bot_reply})

with tab_ovning:
    st.header("Jobb-Övningar")

    exercises = {
        "Sjukvård (hemtjänst)": [
            {"q": "Fyll i: 'Kan du ______ mig med ______?'", "a": ["hjälpa", "toaletten"], "type": "fill"},
            {"q": "Vad säger du?", "options": ["Vill du äta?", "Ska jag diska?", "Är du trött?"], "a": 0, "type": "mc"}
        ],
        "Bygg": [{"q": "Fyll i: 'Vi behöver ______ och ______.'", "a": ["skruvar", "spik"], "type": "fill"}],
        "Restaurang": [{"q": "Fyll i: 'Bord ______ är ______.'", "a": ["tre", "redo"], "type": "fill"}],
        "Lager-logistik": [{"q": "Fyll i: 'Pall ______ går till ______.'", "a": ["A12", "zon B"], "type": "fill"}],
        "Produktion": [{"q": "Fyll i: 'Maskin ______ är ______.'", "a": ["tre", "klar"], "type": "fill"}],
        "Retail": [{"q": "Fyll i: 'Kunden vill ______ i ______.'", "a": ["betala", "kassan"], "type": "fill"}]
    }

    if st.button("Ny övning"):
        ex = random.choice(exercises.get(bransch_val, [{"q": "Inga övningar", "a": [], "type": "text"}]))
        st.session_state.current_exercise = ex
        st.rerun()

    if st.session_state.current_exercise:
        ex = st.session_state.current_exercise
        st.markdown(f"<div class='exercise-box'><b>Övning:</b> {ex['q']}</div>", unsafe_allow_html=True)

        if ex["type"] == "fill":
            ans1 = st.text_input("Första", key="fill1")
            ans2 = st.text_input("Andra", key="fill2")
            if st.button("Kontrollera"):
                if [ans1.lower(), ans2.lower()] == [a.lower() for a in ex["a"]]:
                    st.success("Rätt! +10 poäng")
                    st.session_state.poang += 10
                else:
                    st.error(f"Fel. Rätt: {', '.join(ex['a'])}")

        elif ex["type"] == "mc":
            choice = st.radio("Välj:", ex["options"], key="mc")
            if st.button("Svara"):
                if ex["options"].index(choice) == ex["a"]:
                    st.success("Rätt! +8 poäng")
                    st.session_state.poang += 8
                    if st.button("Hör rätt svar"):
                        tts = gTTS(ex["options"][ex["a"]], lang=mal_codes[mal_val])
                        tts.save("mc.mp3")
                        st.audio("mc.mp3")
                else:
                    st.error("Fel. Försök igen.")

with st.expander("Senaste 5"):
    for h in st.session_state.historik[-5:]:
        st.write(f"**Du:** {h['user']}")
        st.write(f"**Worklingo:** {h['bot']}")
        st.divider()

st.success("KLART! Pusha → Reboot → Sälj för 9€/mån!")
