"""
Streamlit recorder and demo UI for ParkiSense

Upgraded UI: medical theme, standard vs advanced toggle, biomarker table,
waveform, local inference and upload to server. Uses utils.audio_features and
utils.model_inference to keep model/feature logic centralized.
"""

import io
import time
from datetime import datetime
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import requests
import soundfile as sf
import sounddevice as sd
import streamlit as st

from ml.audio_processor import denoise_spectral_subtract, estimate_snr_db
from utils.audio_features import (
    create_feature_vector,
    extract_biomarkers,
    validate_audio_length,
)
from utils.model_inference import predict_from_vector, load_model_and_scaler


# App configuration
st.set_page_config(page_title="AI Parkinson Voice Screening — ParkiSense", layout="centered")

st.markdown("# AI Parkinson Voice Screening")
st.markdown("This is a non-diagnostic research tool — Speak for 4 seconds or upload audio.")
st.info("Guidance: Say 'ahh' for 4 seconds in a quiet room. This app does not store your audio unless you explicitly upload it.")


col1, col2 = st.columns([3, 1])

with col1:
    duration = st.slider("Record duration (seconds)", min_value=2, max_value=10, value=4, step=1)
    sample_rate = st.selectbox("Sample rate (Hz)", options=[16000, 22050, 44100], index=1)
    apply_denoise = st.checkbox("Apply noise reduction (simple spectral subtraction)", value=True)
    debug = st.checkbox("Debug mode (show feature vector)", value=False)
    mode = st.radio("Mode", options=["Standard", "Advanced (Bio-Markers)"], index=0)

with col2:
    st.markdown("### Privacy & Disclaimer")
    st.markdown("**Privacy:** No audio is stored locally by default.\n**Disclaimer:** This is a research prototype, not a medical device.")


API_BASE = st.session_state.get("STREAMLIT_API_URL") or "http://127.0.0.1:8000"
PREDICT_ENDPOINT = "/predict"


record_placeholder = st.empty()
controls = st.empty()


def record_audio(seconds: int, sr: int) -> Optional[np.ndarray]:
    """Record audio from the default microphone for `seconds` seconds (mono).

    Returns the numpy array or None on error.
    """
    try:
        recording = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype="float32")
        sd.wait()
        return np.squeeze(recording)
    except Exception as e:
        st.error(f"Recording failed: {e}")
        return None


def wav_bytes_from_array(y: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, y, sr, format="WAV")
    buf.seek(0)
    return buf.read()


def upload_to_api(wav_bytes: bytes, filename: str = None):
    url = API_BASE + PREDICT_ENDPOINT
    files = {"file": (filename or "recording.wav", wav_bytes, "audio/wav")}
    try:
        resp = requests.post(url, files=files, timeout=60)
        return resp
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None


if "last_wav" not in st.session_state:
    st.session_state["last_wav"] = None
    st.session_state["last_sr"] = None
    st.session_state["snr_before"] = None
    st.session_state["snr_after"] = None


def do_countdown(seconds: int):
    for i in range(seconds, 0, -1):
        record_placeholder.markdown(f"### Recording starts in: {i} ⏱️")
        time.sleep(1)
    record_placeholder.markdown("### Recording... 🎙️")


start = controls.button("Start Recording")
if start:
    do_countdown(3)
    y = record_audio(duration, sample_rate)
    if y is not None:
        st.session_state["last_wav"] = y
        st.session_state["last_sr"] = sample_rate

        # validate
        if not validate_audio_length(y, sample_rate, min_seconds=2.0):
            st.warning("Recording too short. Please record at least 2 seconds.")

        try:
            snr_before = estimate_snr_db(y, sample_rate)
        except Exception:
            snr_before = None
        st.session_state["snr_before"] = snr_before

        if apply_denoise:
            try:
                y_denoised = denoise_spectral_subtract(y, sample_rate)
                snr_after = estimate_snr_db(y_denoised, sample_rate)
                st.session_state["last_wav"] = y_denoised
                st.session_state["snr_after"] = snr_after
            except Exception as e:
                st.warning(f"Denoising failed: {e}")
                st.session_state["snr_after"] = None

        # playback and waveform
        wav_bytes = wav_bytes_from_array(st.session_state["last_wav"], st.session_state["last_sr"])
        st.audio(wav_bytes, format="audio/wav")

        # waveform
        fig, ax = plt.subplots(figsize=(8, 2))
        times = np.linspace(0, len(st.session_state["last_wav"]) / st.session_state["last_sr"], num=len(st.session_state["last_wav"]))
        ax.plot(times, st.session_state["last_wav"], color="#0369A1")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Waveform")
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("Recording metadata")
        duration_sec = round(len(st.session_state["last_wav"]) / st.session_state["last_sr"], 2)
        st.write({
            "sample_rate": st.session_state["last_sr"],
            "duration_seconds": duration_sec,
            "snr_db_before": st.session_state["snr_before"],
            "snr_db_after": st.session_state["snr_after"],
        })

        # features
        vec, feat_names = create_feature_vector(st.session_state["last_wav"], st.session_state["last_sr"])
        biomarkers = extract_biomarkers(st.session_state["last_wav"], st.session_state["last_sr"])

        if debug:
            st.subheader(f"Feature vector (length {len(vec)})")
            st.write({name: (float(v) if not np.isnan(v) else None) for name, v in zip(feat_names, vec)})

        if mode.startswith("Advanced"):
            st.subheader("Extracted Voice Biomarkers")
            st.table(
                {
                    "Mean Pitch (Hz)": biomarkers.get("mean_pitch"),
                    "Max Pitch (Hz)": biomarkers.get("max_pitch"),
                    "Pitch StdDev (Hz)": biomarkers.get("std_pitch"),
                    "Jitter (%)": biomarkers.get("jitter_pct"),
                    "Shimmer (%)": biomarkers.get("shimmer_pct"),
                    "HNR (dB)": biomarkers.get("hnr_db"),
                }
            )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Retry Recording"):
                st.session_state["last_wav"] = None
                st.session_state["last_sr"] = None
                st.session_state["snr_before"] = None
                st.session_state["snr_after"] = None
                st.experimental_rerun()
        with col_b:
            if st.button("Analyze (local model)"):
                with st.spinner("Running local inference..."):
                    try:
                        load_model_and_scaler()
                        result = predict_from_vector(vec)
                        st.success("Inference complete")
                        st.json(result)
                    except Exception as e:
                        st.error(f"Inference failed: {e}")
            if st.button("Upload to API"):
                with st.spinner("Uploading and analyzing on server..."):
                    resp = upload_to_api(wav_bytes, filename="recording.wav")
                    if resp is not None:
                        if resp.status_code == 200:
                            st.success("Server analysis completed")
                            try:
                                st.json(resp.json())
                            except Exception:
                                st.write(resp.text)
                        else:
                            st.error(f"API returned status {resp.status_code}: {resp.text}")
else:
    st.info("Click 'Start Recording' to begin (local microphone required).")
