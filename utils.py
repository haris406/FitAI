import math, csv, os
import streamlit as st

def logo_html():
    return "<h2 style='color:#00FFFF;text-align:center;'>🤖 FitAI</h2>"

def calculate_angle(a, b, c):
    a, b, c = map(lambda p: [p[0], p[1]], [a, b, c])
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return abs(ang if ang > 0 else 360 + ang)

def dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def beep(enable):
    if enable:
        import os
        os.system('echo "\a"')

def speak(count, enable):
    if enable:
        import pyttsx3
        pyttsx3.init().say(str(count))

def save_session(record):
    os.makedirs("data", exist_ok=True)
    with open("data/workout_sessions.csv", "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=record.keys())
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(record)

def load_sessions():
    import pandas as pd
    if os.path.exists("data/workout_sessions.csv"):
        return pd.read_csv("data/workout_sessions.csv")
    else:
        return pd.DataFrame(columns=["timestamp","name","exercise","reps_or_seconds","calories","duration_s"])
