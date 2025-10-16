import streamlit as st
from utils import logo_html

st.set_page_config(page_title="FitAI — Smart Fitness Trainer", page_icon="💪", layout="wide")

# Custom Matte Dark + Neon Teal Theme
st.markdown("""
    <style>
        body {
            background-color: #0D1117;
            color: #E6E6E6;
        }
        .stApp {
            background-color: #0D1117 !important;
        }
        h1, h2, h3, h4 {
            color: #00FFFF !important;
            text-shadow: 0 0 12px #00FFFF80;
        }
        .sidebar .sidebar-content {
            background-color: #0B0F15 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #0B0F15 !important;
        }
        .stMetric label, .stMetric div {
            color: #00FFFF !important;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.page_link("pages/Dashboard.py", label="🏠 Dashboard")
    st.page_link("pages/Workout.py", label="💥 Workout")
    st.page_link("pages/History.py", label="📊 History")
    st.page_link("pages/Insights.py", label="📈 Insights")
    st.page_link("pages/Settings.py", label="⚙️ Settings")

# Center Content
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.image("assets/logo.png", width=180)
st.markdown("<h1>Welcome to FitAI — Smart Fitness Trainer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:lightgray;'>Choose <b>Workout</b> from sidebar to start live tracking using your webcam.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.write("---")
st.markdown("<p style='text-align:center; color:#00FFFF;'>© 2025 FitAI — by Haris</p>", unsafe_allow_html=True)
