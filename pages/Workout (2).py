# pages/Workout.py
import streamlit as st
import cv2
import mediapipe as mp
import time
from datetime import datetime
from utils import logo_html, calculate_angle, dist, save_session, beep, speak

st.markdown(logo_html(), unsafe_allow_html=True)
st.title("Workout — Live Tracking")

# session defaults
st.session_state.setdefault("running", False)
st.session_state.setdefault("counter", 0)
st.session_state.setdefault("stage", None)
st.session_state.setdefault("start_time", None)
st.session_state.setdefault("camera_index", 0)
st.session_state.setdefault("beep_enabled", True)
st.session_state.setdefault("voice_enabled", False)

exercise = st.selectbox("Exercise", ["Push-ups", "Squats", "Jumping Jacks", "Plank", "Bicep Curls"])
target = st.number_input("Target (reps or seconds)", 3, 2000, 12)

left, right = st.columns([2,1])
video = left.empty()
with right:
    st.metric("Count", int(st.session_state.counter))
    st.checkbox("Beep (Windows)", value=st.session_state.beep_enabled, key="beep_enabled")
    st.checkbox("Voice feedback", value=st.session_state.voice_enabled, key="voice_enabled")
    if st.button("Start"):
        st.session_state.running = True
        st.session_state.counter = 0
        st.session_state.stage = "up"
        st.session_state.start_time = time.time()
    if st.button("Stop"):
        st.session_state.running = False

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

if st.session_state.running:
    cam_idx = int(st.session_state.camera_index)
    cap = cv2.VideoCapture(cam_idx)
    if not cap.isOpened():
        st.error(f"Camera {cam_idx} not available. Try Settings.")
        st.session_state.running = False
    else:
        with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
            last_rep = 0
            smoothing = 0.45
            smoothed = None
            while st.session_state.running:
                ret, frame = cap.read()
                if not ret:
                    st.error("Camera frame not received.")
                    break
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = pose.process(rgb)
                status = "No person"
                metric = 0
                try:
                    if res.pose_landmarks:
                        lm = res.pose_landmarks.landmark
                        def P(i): return [lm[i].x, lm[i].y]
                        l_sh, r_sh = P(11), P(12)
                        l_el, r_el = P(13), P(14)
                        l_wr, r_wr = P(15), P(16)
                        l_hip, r_hip = P(23), P(24)
                        l_knee, r_knee = P(25), P(26)
                        l_ank, r_ank = P(27), P(28)
                        now = time.time()

                        if exercise == "Push-ups":
                            left_el = calculate_angle(l_sh, l_el, l_wr)
                            right_el = calculate_angle(r_sh, r_el, r_wr)
                            avg = (left_el + right_el)/2.0
                            smoothed = avg if smoothed is None else smoothing*avg + (1-smoothing)*smoothed
                            metric = int(smoothed)
                            if smoothed > 160: st.session_state.stage = "up"; status = "Up"
                            if smoothed < 95 and st.session_state.stage=="up" and (now-last_rep>0.8):
                                st.session_state.counter += 1
                                last_rep = now
                                st.session_state.stage = "down"
                                status = f"Rep {st.session_state.counter}"
                                if st.session_state.beep_enabled: beep(True)
                                if st.session_state.voice_enabled: speak(st.session_state.counter, True)

                        elif exercise == "Squats":
                            left_k = calculate_angle(l_hip, l_knee, l_ank)
                            right_k = calculate_angle(r_hip, r_knee, r_ank)
                            avgk = (left_k+right_k)/2.0; metric = int(avgk)
                            if avgk > 160: st.session_state.stage="up"; status="Stand"
                            if avgk < 95 and st.session_state.stage=="up" and (now-last_rep>0.8):
                                st.session_state.counter += 1; last_rep=now; st.session_state.stage="down"; status=f"Squat {st.session_state.counter}"

                        elif exercise == "Jumping Jacks":
                            hipw = dist(l_hip, r_hip) if dist(l_hip,r_hip)>1e-6 else 0.25
                            rel_h = dist(l_wr,r_wr)/hipw; rel_l = dist(l_ank,r_ank)/hipw
                            metric = int(rel_h*100)
                            if rel_h < 1.05 and rel_l < 1.0: st.session_state.stage="close"
                            if rel_h > 1.6 and rel_l > 1.2 and st.session_state.stage=="close" and (now-last_rep>0.6):
                                st.session_state.counter +=1; last_rep=now; st.session_state.stage="open"; status=f"Jack {st.session_state.counter}"

                        elif exercise == "Plank":
                            left_b = calculate_angle(l_sh, l_hip, l_ank)
                            right_b = calculate_angle(r_sh, r_hip, r_ank)
                            avgb = (left_b+right_b)/2.0; metric=int(avgb)
                            if avgb > 140:
                                st.session_state.counter = int(time.time()-st.session_state.start_time)
                                status = f"Plank: {st.session_state.counter}s"
                            else:
                                status = "Fix plank"

                        elif exercise == "Bicep Curls":
                            left_el = calculate_angle(l_sh, l_el, l_wr)
                            right_el = calculate_angle(r_sh, r_el, r_wr)
                            avg = (left_el + right_el) / 2.0
                            smoothed = avg if smoothed is None else smoothing * avg + (1 - smoothing) * smoothed
                            metric = int(smoothed)
                            if smoothed > 160:
                                st.session_state.stage = "down"
                                status = "Down"
                            if smoothed < 45 and st.session_state.stage == "down" and (now - last_rep > 0.8):
                                st.session_state.counter += 1
                                last_rep = now
                                st.session_state.stage = "up"
                                status = f"Curl {st.session_state.counter}"
                                if st.session_state.beep_enabled: beep(True)
                                if st.session_state.voice_enabled: speak(st.session_state.counter, True)

                        mp_draw.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    else:
                        status = "No person"
                except Exception:
                    status = "No landmarks"

                cv2.putText(frame, exercise, (12,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,200,255), 2)
                cv2.putText(frame, f"Count: {st.session_state.counter}", (12,70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,125), 2)
                cv2.putText(frame, f"Status: {status}", (12,110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230,230,230), 2)
                if metric: cv2.putText(frame, f"Metric: {metric}", (12,146), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,255), 1)
                video.image(frame, channels="BGR", use_column_width=True)

                if exercise!="Plank" and st.session_state.counter >= target:
                    elapsed = int(time.time() - st.session_state.start_time)
                    rec = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           "name":"User", "exercise": exercise, "reps_or_seconds": st.session_state.counter,
                           "calories": 0, "duration_s": elapsed}
                    save_session(rec)
                    st.success(f"Target reached: {st.session_state.counter} — saved.")
                    st.session_state.running = False
                    break

                time.sleep(0.02)
        cap.release()
