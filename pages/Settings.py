import streamlit as st
from utils import logo_html

st.markdown(logo_html(), unsafe_allow_html=True)
st.title("⚙️ Settings")

st.slider("Camera Index", 0, 3, key="camera_index")
st.checkbox("Beep Enabled", value=True, key="beep_enabled")
st.checkbox("Voice Feedback", value=False, key="voice_enabled")

st.success("✅ Settings saved automatically.")
