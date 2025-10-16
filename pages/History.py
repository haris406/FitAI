import streamlit as st
import pandas as pd
from datetime import datetime
from utils import load_sessions, logo_html

st.set_page_config(page_title="Workout History", page_icon="📊", layout="wide")

# --- Custom Style ---
st.markdown("""
    <style>
        body { background-color: #0D1117; color: #E6E6E6; }
        .neon { color: #00FFFF; text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF; }
        .stDataFrame { border: 1px solid #00FFFF; border-radius: 10px; }
        [data-testid="stSidebar"] { background-color: #0B0F15 !important; }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown(f"""
    <div style="text-align:center; margin-top:-30px;">
        {logo_html()}
        <h1 class="neon">🏋️ Workout History</h1>
        <p style="color:#888;">View and filter your saved workout sessions</p>
        <hr style="border:1px solid #00FFFF;">
    </div>
""", unsafe_allow_html=True)

# --- Load Data ---
data = load_sessions()

if data is None or data.empty:
    st.info("No history yet. Complete a few workouts first to see results here.")
    st.stop()

# Convert date
if "timestamp" in data.columns:
    data["date"] = pd.to_datetime(data["timestamp"]).dt.date

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔎 Filters")
    exercises = sorted(data["exercise"].unique().tolist())
    selected = st.multiselect("Exercise Type", exercises, default=exercises)
    min_date, max_date = data["date"].min(), data["date"].max()
    date_range = st.date_input("Date Range", [min_date, max_date])

# Apply filters
filtered = data[
    (data["exercise"].isin(selected)) &
    (data["date"].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])))
]

# --- Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Sessions", len(filtered))
col2.metric("Total Reps / Secs", int(filtered["reps_or_seconds"].sum()))
col3.metric("Total Duration (s)", int(filtered["duration_s"].sum()))

st.divider()

# --- Table ---
st.markdown("<h3 class='neon'>📋 Session Details</h3>", unsafe_allow_html=True)
st.dataframe(filtered.sort_values("timestamp", ascending=False), use_container_width=True)

# --- Download ---
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download History CSV", csv, "workout_history.csv", "text/csv")

# --- Footer ---
st.markdown("<hr><center style='color:#00FFFF;'>© 2025 FitAI — by Haris</center>", unsafe_allow_html=True)
