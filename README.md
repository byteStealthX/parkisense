# 🧠 ParkiSense

**ParkiSense** is a next-generation medical-tech web app that predicts early **Parkinson’s disease risk** from **voice recordings**.  
Changes in speech patterns often occur before visible motor symptoms — ParkiSense leverages this insight to help enable early detection and awareness.

> ⚠️ *Disclaimer:* This is a **prototype and research project**, **not a medical diagnostic tool**.  
Always consult qualified healthcare professionals for medical advice.

---

## 🌐 Live Demo

👉 https://parkisense-id60pmmk7-coder671s-projects.vercel.app

---

## ✨ Features

- 🎙️ **Record or Upload Voice:** Capture or upload short audio samples (3–10 seconds)
- 🧩 **Machine Learning Analysis:** Detect early Parkinson’s risk using trained ML models
- 📊 **Feature Extraction:** MFCCs, jitter, shimmer, pitch, and harmonic ratios
- 🌈 **Interactive Visuals:** Waveform, spectrogram, and prediction confidence graphs
- 💾 **Data Handling:** Local or optional cloud-stored results
- 🧠 **Futuristic UI:** Minimal, medical-grade aesthetic inspired by modern health apps

---

## 🧰 Tech Stack

| Layer | Technologies |
|:------|:-------------|
| **Frontend** | Next.js (App Router), React, Tailwind CSS |
| **Backend / API** | Node.js, Express, or Next.js API routes |
| **ML Model** | Python (scikit-learn / TensorFlow / PyTorch) |
| **Audio Processing** | Web Audio API / Meyda / librosa |
| **Deployment** | Vercel (frontend + API), Railway / Render (backend) |

---

## 📂 Project Structure
parkisense/
├── app/ # Next.js App Router pages and API routes
├── components/ # Reusable UI components
├── public/ # Static assets and icons
├── model/ # Trained ML model (e.g., model.pkl)
├── scripts/ # Audio preprocessing and training scripts
├── utils/ # Helper functions
└── README.md



