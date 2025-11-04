import streamlit as st

st.title("WORKLINGO v3.0")
st.write("**Grattis! Appen fungerar!**")

bransch = st.selectbox("Bransch", ["Bygg", "Sjukvård", "Hotell"])
nivå = st.selectbox("Nivå", ["Nybörjare", "Mellan", "Avancerad"])

if st.button("Skapa övning"):
    st.write("**Genererad övning:**")
    st.write("1. Vad heter 'hammer' på svenska?")
    st.write("   → **Hammare**")
    st.write("2. Vad heter 'spik' på svenska?")
    st.write("   → **Spik**")
    st.session_state.xp = st.session_state.get('xp', 0) + 10
    st.write(f"**XP:** {st.session_state.xp}")