import streamlit as st
from utils import load_sessions, logo_html

# --- Logo centered + highlighted
st.markdown(
    f"""
    <div style="text-align:center; margin-top:-40px;">
        {logo_html()}
        <h1 style="color:#00FFD1; font-size:40px; margin-bottom:0;">🏠 FitAI Dashboard</h1>
        <p style="color:#888; font-size:16px;">Track your workout performance & progress</p>
        <hr style="border:1px solid #00FFD1; margin-top:10px;">
    </div>
    """,
    unsafe_allow_html=True
)

# --- Load user workout data
data = load_sessions()

if data is not None and not data.empty:
    total_sessions = len(data)
    total_reps = int(data["reps_or_seconds"].sum())
    total_cal = int((data["reps_or_seconds"] * 0.5).sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("🏋️ Total Sessions", total_sessions)
    col2.metric("🔥 Total Reps", total_reps)
    col3.metric("⚡ Calories Burned", total_cal)

    st.markdown("### 📊 Workout Distribution")
    st.bar_chart(data.groupby("exercise")["reps_or_seconds"].sum())

else:
    st.info("No workout data yet. Start your first session in the **Workout** page to see insights here!")

# --- AI Recommendation & Personalization (Pro) ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

st.markdown("## 🧠 Smart Personalized Plan", unsafe_allow_html=True)

def compute_trend(series):
    # series: pandas Series indexed by date with numeric values
    if len(series) < 2:
        return 0.0
    # convert dates to ordinal
    x = np.arange(len(series))
    y = series.values.astype(float)
    try:
        m, c = np.polyfit(x, y, 1)  # slope
        return float(m)
    except Exception:
        return 0.0

def recommend_from_history(df):
    # Expecting columns: timestamp, exercise, reps_or_seconds, duration_s
    df = df.copy()
    if df.empty:
        return {"note": "No data yet — do a few workouts to unlock recommendations."}

    # ensure types
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    recent_cutoff = (df["timestamp"].max() - pd.Timedelta(days=21))
    recent = df[df["timestamp"] >= recent_cutoff]

    # 1) Average & total by exercise
    stats = df.groupby("exercise")["reps_or_seconds"].agg(["mean","median","sum","count"]).rename(columns={
        "mean":"avg","median":"med","sum":"total","count":"sessions"
    })

    # 2) identify weakest & strongest (by average)
    avg_sorted = stats["avg"].sort_values()
    weakest = avg_sorted.index[0] if not avg_sorted.empty else None
    strongest = avg_sorted.index[-1] if not avg_sorted.empty else None

    # 3) Trend per exercise (using last 21 days)
    trends = {}
    for ex in df["exercise"].unique():
        series = (df[df["exercise"]==ex]
                  .groupby("date")["reps_or_seconds"]
                  .mean()
                  .sort_index())
        trends[ex] = compute_trend(series)

    # 4) Recent consistency (how many sessions in last 21 days)
    recent_counts = recent.groupby("exercise")["reps_or_seconds"].count().to_dict()

    # 5) Suggest next-session targets:
    next_targets = {}
    for ex in stats.index:
        base = float(stats.loc[ex, "avg"])
        # If trending up, keep moderate bump; if trending down, keep small bump or maintain
        slope = trends.get(ex, 0.0)
        if slope > 0.2:
            bump = 1.10  # +10%
        elif slope < -0.2:
            bump = 1.03  # +3%
        else:
            bump = 1.06  # +6%
        # plank-like exercises store seconds — we still treat as numeric
        suggested = max(1, int(round(base * bump)))
        next_targets[ex] = suggested

    # 6) 7-day mini plan (3 sessions/week balanced)
    # Prioritize weakest (2 sessions), then mix strongest + one other
    exercises = list(stats.index)
    plan = []
    wk = 0
    days = []
    today = datetime.now().date()
    # pick two other exercises (not weakest) for variety
    others = [e for e in exercises if e != weakest]
    # build 3 sessions in coming 7 days
    for d in range(7):
        day = today + timedelta(days=d)
        # schedule on Mon/Wed/Fri-ish -> choose roughly every 2-3 days
        if len(plan) >= 3:
            break
        # simple distribution: day indices 0..6 -> pick 1,3,5
        if d in [0,2,4]:  # today, +2, +4
            if len(plan) == 0:
                sess_ex = weakest
            elif len(plan) == 1:
                sess_ex = others[0] if others else weakest
            else:
                sess_ex = strongest if strongest else weakest
            recommended_reps = next_targets.get(sess_ex, 10)
            plan.append({
                "date": day.strftime("%Y-%m-%d"),
                "exercise": sess_ex,
                "recommended_reps_or_secs": recommended_reps,
                "note": "Focus on form + controlled tempo"
            })

    # 7) short textual recommendation
    rec_text = []
    rec_text.append(f"Your weakest exercise is **{weakest}** (avg {stats.loc[weakest,'avg']:.1f}).")
    rec_text.append(f"Your strongest exercise is **{strongest}** (avg {stats.loc[strongest,'avg']:.1f}).")
    # trend summary
    improving = [e for e,s in trends.items() if s > 0.2]
    declining = [e for e,s in trends.items() if s < -0.2]
    if improving:
        rec_text.append(f"Improving recently at: {', '.join(improving)}.")
    if declining:
        rec_text.append(f"Needs attention (declining): {', '.join(declining)}.")
    rec_text.append("Next session targets provided below. Aim for consistent form — not speed.")

    return {
        "stats": stats.reset_index(),
        "weakest": weakest,
        "strongest": strongest,
        "trends": trends,
        "next_targets": next_targets,
        "mini_plan": plan,
        "note": "Auto-generated from your last sessions (local).",
        "text": "\n".join(rec_text)
    }

# run recommender
rec = recommend_from_history(data if 'data' in locals() else pd.DataFrame())

if "note" in rec and rec.get("stats", None) is None:
    st.info(rec["note"])
else:
    st.info(rec["text"])
    # show small stats table
    st.markdown("### 📌 Per-exercise averages & sessions")
    st.dataframe(rec["stats"].rename(columns={
        "avg":"Avg Reps/Secs", "med":"Median", "total":"Total", "sessions":"Sessions"
    }), use_container_width=True)

    # next targets
    st.markdown("### 🎯 Next-session Targets")
    nt_df = pd.DataFrame([
        {"exercise":k, "suggested_reps_or_secs":v} for k,v in rec["next_targets"].items()
    ]).sort_values("exercise")
    st.table(nt_df)

    # mini plan
    st.markdown("### 🗓️ 7-day Mini Plan (3 sessions)")
    plan_df = pd.DataFrame(rec["mini_plan"])
    st.dataframe(plan_df, use_container_width=True)

    # quick action buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Save Mini Plan as CSV"):
            csv = plan_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Plan CSV", csv, "fitai_mini_plan.csv", "text/csv")
    with col_b:
        if st.button("Apply Targets to Next Workout (sets)"):
            st.success("Targets applied to memory — next Workout session will show updated target suggestions (local only).")
            # store in session_state for Workout page to read (optional)
            st.session_state["fitai_targets"] = rec["next_targets"]

# --- end AI recommendation

# --- Footer
st.markdown(
    "<hr><center style='color:gray;'>© 2025 FitAI — by Haris</center>",
    unsafe_allow_html=True
)
