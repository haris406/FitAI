import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import load_sessions, logo_html

st.markdown(logo_html(), unsafe_allow_html=True)
st.title("📈 Insights")

data = load_sessions()
if not data.empty:
    st.subheader("Average Reps by Exercise")
    avg = data.groupby("exercise")["reps_or_seconds"].mean()
    st.bar_chart(avg)

    st.subheader("Calories Trend")
    data["date"] = pd.to_datetime(data["timestamp"]).dt.date
    daily = data.groupby("date")["reps_or_seconds"].sum()
    st.line_chart(daily)
else:
    st.info("No data to generate insights yet.")
