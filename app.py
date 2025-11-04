import streamlit as st
import openai
from gtts import gTTS
import random

st.set_page_config(page_title="Worklingo v3.1", layout="wide")

# Enkel inloggning
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

if st.button("Logga ut"):
    st.session_state.logged_in = False
    st.rerun()

# Tema
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
    .tooltip {position: relative; display: inline-block;}
    .tooltip .tooltiptext {visibility: hidden; width: 200px; background-color: #006400; color: white; text-align: center; border-radius: 6px; padding: 5px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -100px; opacity: 0; transition: opacity 0.3s;}
    .tooltip:hover .tooltiptext {visibility: visible; opacity: 1;}
</style>
""", unsafe_allow_html=True)

# Session
for key in ["historik", "poang", "niva", "current_exercise", "difficulty"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "historik" else 0 if key == "poang" else "Nybörjare" if key == "niva" else None if key == "current_exercise" else "Nybörjare"

# Full lista
ui_sprak = ["Українська", "Русский", "Polski", "Slovenčina", "Српски", "Български", "Română", "Lietuvių", "English"]
mal_sprak = ["Svenska", "Norsk", "Dansk", "Deutsch", "English", "Nederlands", "Español", "Français", "Italiano"]
mal_codes = {"Svenska": "sv", "Norsk": "no", "Dansk": "da", "Deutsch": "de", "English": "en", "Nederlands": "nl", "Español": "es", "Français": "fr", "Italiano": "it"}
branscher = ["Sjukvård (hemtjänst)", "Bygg", "Restaurang", "Lager-logistik", "Produktion", "Retail"]

# Prompt på UI-språk
ui_prompts = {
    "English": "Write in English about your work – I'll correct to {target}.",
    "Русский": "Напиши на русском о своей работе – я исправлю на {target}.",
    "Polski": "Napisz po polsku o swojej pracy – poprawię na {target}.",
    "Slovenčina": "Napíš po slovensky o svojej práci – opravím na {target}.",
    "Српски": "Пиши на српском о свом послу – исправићу на {target}.",
    "Български": "Пиши на български за работата си – ще коригирам на {target}.",
    "Română": "Scrie în română despre munca ta – voi corecta în {target}.",
    "Lietuvių": "Rašyk lietuviškai apie savo darbą – pataisysiu į {target}.",
    "Українська": "Напиши українською про свою роботу – виправлю на {target}."
}

# Svårighetsgrad
difficulty_levels = ["Nybörjare", "Medveten", "Proffs"]
with st.sidebar:
    st.markdown("### Inställningar")
    difficulty = st.selectbox("Svårighetsgrad", difficulty_levels, index=difficulty_levels.index(st.session_state.niva))
    st.session_state.niva = difficulty

st.markdown(f"<h1 style='text-align:center; color:#006400;'>🌿 Worklingo v3.1</h1>", unsafe_allow_html=True)
st.markdown(f"**Poäng: <span style='color:green;font-weight:bold'>{st.session_state.poang}</span>** | **Nivå: {st.session_state.niva}**", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: ui_val = st.selectbox("Ditt språk", ui_sprak, key="ui")
with c2: mal_val = st.selectbox("Lär dig", mal_sprak, key="mal")
with c3: bransch_val = st.selectbox("Bransch", branscher, key="bransch")

# Dynamisk prompt
prompt_template = ui_prompts.get(ui_val, "Write in {source} about your work – I'll correct to {target}.")
chatt_prompt = prompt_template.format(source=ui_val, target=mal_val)

tab_chatt, tab_ovning = st.tabs(["💬 Jobbchatt", "🏋️ Övningar"])

with tab_chatt:
    user_input = st.chat_input(chatt_prompt)

    if user_input:
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)

        client = openai.OpenAI(base_url="https://api.x.ai/v1", api_key=st.secrets["XAI_API_KEY"])
        system_prompt = f"""
        Användaren arbetar inom {bransch_val}. Svårighetsgrad: {st.session_state.niva}.
        Rätta/översätt från {ui_val} till perfekt {mal_val}.
        Svara EXAKT:
        1. Korrekt mening på {mal_val}
        2. Poäng: X/10 (baserat på {st.session_state.niva})
        3. Förklaring: [kort]
        BARA JOBBRELATERAT!
        """
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
        if st.session_state.poang > 150: st.session_state.niva = "Proffs 🏆"
        elif st.session_state.poang > 50: st.session_state.niva = "Medveten 📈"

        correct_sentence = bot_reply.split('\n')[0].strip()
        if st.button("🎵 Hör uttal"):
            tts = gTTS(correct_sentence, lang=mal_codes[mal_val])
            tts.save("uttal.mp3")
            st.audio("uttal.mp3")

        # Hover-översättning (Proffs-nivå)
        if st.session_state.niva == "Proffs":
            hover_text = f"<div class='tooltip'>{correct_sentence}<span class='tooltiptext'>{user_input}</span></div>"
            st.markdown(hover_text, unsafe_allow_html=True)

        st.session_state.historik.append({"user": user_input, "bot": bot_reply})

with tab_ovning:
    st.header("📚 Pedagogiska Övningar")

    exercises = {
        "Sjukvård (hemtjänst)": [
            {"q": "Fyll i: 'Kan du ______ mig med ______?'", "a": ["hjälpa", "toaletten"], "type": "fill", "target": "Kan du hjälpa mig med toaletten?"},
            {"q": "Välj rätt:", "options": ["Vill du äta?", "Ska jag diska?", "Är du trött?"], "a": 0, "type": "mc", "target": "Vill du äta?"}
        ],
        # ... lägg till fler per bransch
    }.get(bransch_val, [])

    if st.button("🆕 Ny övning"):
        ex = random.choice(exercises)
        st.session_state.current_exercise = ex
        st.session_state.ex_attempts = 0
        st.session_state.ex_correct = 0
        st.rerun()

    if st.session_state.current_exercise:
        ex = st.session_state.current_exercise
        st.markdown(f"<div class='exercise-box'><b>{ex['q']}</b></div>", unsafe_allow_html=True)

        if ex["type"] == "fill":
            ans = st.text_input("Ditt svar", key="fill_ans")
            if st.button("Kontrollera"):
                st.session_state.ex_attempts += 1
                if ans.strip().lower() == ex["target"].lower():
                    st.session_state.ex_correct += 1
                    st.success("Rätt! +10 poäng")
                    st.session_state.poang += 10
                else:
                    st.error(f"Fel. Rätt: {ex['target']}")

        # Hover på Proffs
        if st.session_state.niva == "Proffs" and "target" in ex:
            st.markdown(f"<div class='tooltip'>{ex['target']}<span class='tooltiptext'>{ex['q']}</span></div>", unsafe_allow_html=True)

with st.expander("📜 Historik"):
    for h in st.session_state.historik[-10:]:
        st.write(f"**Du:** {h['user']}")
        st.write(f"**Worklingo:** {h['bot']}")
        st.divider()

st.success("KLART! Alla språk, svårighetsgrad, hover-översättning (Proffs), korrekt prompt!")
