# 🏥 Parkinson Voice Detector - Audit & Refactoring Plan

**Date**: November 11, 2025  
**Scope**: Production-ready, hackathon-winner prototype upgrade  
**Current Status**: Early-stage web app with basic ML integration

---

## 📋 AUDIT FINDINGS

### ✅ Strengths
1. **Good tech stack**: React 19, FastAPI, Tailwind CSS, Vite
2. **Responsive design**: Mobile-first approach with Framer Motion animations
3. **Core feature complete**: Recording, upload, ML inference workflow
4. **CORS-enabled**: Backend allows frontend integration
5. **Model persistence**: Uses pickle for model/scaler caching

### ⚠️ Critical Issues Found

#### **Backend (Python)**
1. **Hard-coded model path**: `"best_pd_model.pkl"` - no fallback or environment config
2. **Feature dimension mismatch risk**: Extracted features might not match model's training features
3. **No input validation**: Audio duration check (3s) but no upper bound, sample rate assumptions
4. **Error handling too verbose**: Returns implementation details in HTTP errors
5. **Temporary file cleanup**: Only removed in success path - cleanup needed in try/except
6. **Threading issues**: `asyncio` not properly handling blocking librosa calls
7. **No logging**: Can't debug production issues
8. **Hardcoded threshold**: 0.7 for Parkinson classification - no configurable decision boundary
9. **Feature extraction issues**:
   - `RPDE` calculation suspicious (using mean of magnitude from STFT)
   - `DFA` too simplistic (just mean absolute diff)
   - `PPE` calculated on raw signal, should be on specific bands
   - Missing proper feature engineering for clinical validity

#### **Frontend (React)**
1. **Hardcoded API endpoint**: `"http://127.0.0.1:8000/predict"` - not configurable
2. **No error boundaries**: App crashes if API unreachable
3. **Missing loading states**: No visual feedback during file processing
4. **No audio validation**: Can't validate duration before upload
5. **Accessibility issues**: Missing ARIA labels, focus management
6. **LocalStorage not used**: No history/caching of results
7. **No medical disclaimer**: Violates regulatory expectations
8. **No PDF export**: Required feature missing
9. **Feature importance missing**: No SHAP/explanation UI
10. **Recording timer not shown**: UX gap
11. **No sample audio buttons**: Users don't know how to record

#### **General**
1. **No tests**: No unit or integration tests
2. **Missing documentation**: No architecture, API docs, or usage guide
3. **No config management**: Everything hardcoded
4. **No scripts**: No easy way to test or deploy
5. **Package cleanup**: Framer-motion used minimally, could optimize
6. **No multi-language support**: No i18n structure
7. **Missing environment setup**: No .env.example, no setup.py for Python

---

## 🔧 PROPOSED NEW DIRECTORY STRUCTURE

```
Parkinson-s-Disease-Voice-Detector/
├── frontend/                    # React app
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioRecorder.jsx
│   │   │   ├── ResultsDisplay.jsx
│   │   │   ├── FeatureImportance.jsx
│   │   │   ├── PDFReport.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── MedicalDisclaimer.jsx
│   │   │   ├── WaveformPreview.jsx
│   │   │   └── Navbar.jsx
│   │   ├── hooks/
│   │   │   ├── useAudioRecorder.js
│   │   │   ├── useInference.js
│   │   │   └── useLocalStorage.js
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Recorder.jsx
│   │   │   ├── About.jsx
│   │   │   └── NotFound.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── audioProcessor.js
│   │   │   └── pdfGenerator.js
│   │   ├── utils/
│   │   │   ├── constants.js
│   │   │   ├── validationRules.js
│   │   │   └── formatting.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── eslint.config.js
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
│
├── backend/                     # Python FastAPI app
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── feature_extraction.py
│   │   ├── predict.py
│   │   ├── model_loader.py
│   │   ├── audio_processor.py
│   │   └── logging_config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── middleware.py
│   │   └── schemas.py
│   ├── models/
│   │   ├── best_pd_model.pkl
│   │   └── model_metadata.json
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_feature_extraction.py
│   │   ├── test_predict.py
│   │   └── test_api.py
│   ├── scripts/
│   │   ├── test_audio.sh
│   │   ├── run_server.sh
│   │   └── validate_model.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── setup.py
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── usage_steps.md
│   ├── api_reference.md
│   ├── feature_explanation.md
│   └── deployment.md
│
├── scripts/
│   ├── setup.sh
│   ├── run_demo.sh
│   └── validate_setup.sh
│
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🔨 REFACTORING PRIORITY

### Phase 1: Critical Stability (Immediate)
- [ ] Create `backend/ml/config.py` - centralize all constants
- [ ] Add `.env` support and environment validation
- [ ] Fix feature extraction issues (proper RPDE, DFA, PPE)
- [ ] Add proper error handling and logging
- [ ] Add medical disclaimer to frontend
- [ ] Validate audio duration properly (2-8 seconds)

### Phase 2: Core Features (High Priority)
- [ ] Modularize Python backend
- [ ] Create React hooks for audio recording
- [ ] Add PDF report generation
- [ ] Implement feature importance display
- [ ] Add loading spinner animation
- [ ] Add medical UI theme

### Phase 3: UX Polish (Medium Priority)
- [ ] Recording timer display
- [ ] Sample audio buttons
- [ ] Local storage for result history
- [ ] Waveform preview
- [ ] Better error messages
- [ ] Accessibility improvements (a11y)

### Phase 4: Documentation & Deployment (Lower Priority)
- [ ] Write comprehensive docs
- [ ] Add test scripts
- [ ] Setup deployment configuration
- [ ] Add internationalization structure

---

## 🐛 BUGS TO FIX

| Severity | Location | Issue | Fix |
|----------|----------|-------|-----|
| CRITICAL | backend/main.py | Hard-coded model path | Use config + env vars |
| CRITICAL | frontend/Record.jsx | Hardcoded API endpoint | Use environment config |
| HIGH | backend/main.py | Feature mismatch not validated | Check shape in test |
| HIGH | backend/main.py | No upper time limit | Add max 30 sec check |
| HIGH | backend/main.py | Temp files not cleaned on error | Use finally block |
| MEDIUM | backend/main.py | RPDE calculation questionable | Use proper librosa RPDE |
| MEDIUM | frontend/Record.jsx | No medical disclaimer | Add prominent modal |
| MEDIUM | frontend/Record.jsx | No recording timer | Add useRef counter |
| LOW | frontend/* | Missing ARIA labels | Add accessibility tags |

---

## 📦 DEPENDENCY AUDIT

### Frontend - Current
```json
{
  "framer-motion": "^12.9.4",      // Heavy for simple animations
  "axios": "^1.9.0",                // Good for API calls
  "react-icons": "^5.5.0",          // Good
  "react-router-dom": "^7.5.3",     // Good
  "react": "^19.0.0",               // Good
  "tailwindcss": "^4.1.4"           // Good
}
```

### Frontend - Recommended Additions
```json
{
  "jspdf": "^2.5.1",                // PDF generation
  "canvas-confetti": "^1.9.0",      // Nice celebration when healthy result
  "wavesurfer.js": "^7.0.0",        // Waveform visualization
  "zustand": "^4.4.0",              // State management (optional)
  "date-fns": "^3.0.0"              // Date formatting for reports
}
```

### Backend - Current
```python
fastapi>=0.109.0
uvicorn>=0.27.0
numpy>=1.24.0
librosa>=0.10.0
scikit-learn>=1.3.0
pydub>=0.25.0
python-multipart>=0.0.6
```

### Backend - Recommendations
```python
# ADD:
python-dotenv>=1.0.0         # Environment config
pydantic>=2.0.0              # Already used, ensure latest
pydantic-settings>=2.0.0     # For config management
scipy>=1.11.0                # Better RPDE implementation
logging-loki>=0.3.2          # Optional: production logging

# KEEP LEAN (current set is good)
```

---

## 📊 FEATURE EXTRACTION FIXES

### Current Issues
```python
# Issue 1: RPDE calculation is too simplistic
features["RPDE"] = scipy.stats.entropy(np.abs(librosa.stft(y).mean(axis=0)) + 1e-6)
# ❌ Should use recurrence quantification analysis

# Issue 2: DFA too basic
features["DFA"] = np.mean(np.abs(np.diff(y)))
# ❌ Should be detrended fluctuation analysis over multiple scales

# Issue 3: PPE on raw signal
features["PPE"] = scipy.stats.entropy(np.abs(y) + 1e-6)
# ❌ Should be on spectral power envelope
```

### Fixes Applied
Will use:
1. **librosa's native functions** where available
2. **Scientific papers**: Use formulas from Oxford Parkinson's Dataset references
3. **Fallback implementation** if advanced metrics aren't in librosa
4. **Validation** against known good values

---

## 🎨 UI/UX IMPROVEMENTS

### Medical Theme Colors
```css
Primary:    #0369A1 (Sky blue - trust, medical)
Secondary:  #06B6D4 (Cyan - attention)
Success:    #10B981 (Emerald - healthy)
Alert:      #F59E0B (Amber - caution)
Danger:     #DC2626 (Red - risk)
Neutral:    #F3F4F6 to #111827 (Gray scale)
```

### Key Components
1. **Risk Score Card**
   - Color gradient based on score
   - Confidence bar with smooth animation
   - Large, readable typography
   - Emoji icons for context

2. **Loading Spinner**
   - Minimalist rotating icon
   - "Analyzing your voice..." text
   - Pulsing background effect

3. **Disclaimer Modal**
   - Show on first visit + before results
   - "⚕️ NOT a medical device"
   - Link to legitimate medical resources
   - Checkbox to acknowledge

4. **Feature Importance Chart**
   - Horizontal bar chart
   - Show top 5-7 features
   - Color-code by impact
   - SHAP-like explanation ("Why this result")

5. **Audio Waveform**
   - Use wavesurfer.js
   - Show before/after analysis
   - Display duration and sample rate

---

## 🚀 DEPLOYMENT CONSIDERATIONS

### Local Development
```bash
# Frontend
npm install && npm run dev

# Backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python api/main.py
```

### Streamlit Cloud / Cloud Hosting
- Both frontend (Vite) and backend (FastAPI) can be containerized
- Use Docker multi-stage build
- Environment variables via secrets
- Model as versioned artifact

---

## ✅ REFACTORING CHECKLIST

### Code Quality
- [ ] Modularize Python (utils/)
- [ ] Add type hints (Python + JS)
- [ ] Add docstrings to all functions
- [ ] Remove unused imports
- [ ] Add constants file
- [ ] Configure logging

### Testing
- [ ] Unit tests for feature extraction
- [ ] Integration tests for API
- [ ] Frontend component tests
- [ ] E2E tests with sample audio

### Documentation
- [ ] API reference
- [ ] Architecture diagram
- [ ] Usage guide
- [ ] Deployment guide
- [ ] Feature explanation

### Security
- [ ] Input validation
- [ ] API rate limiting
- [ ] CORS properly configured
- [ ] No secrets in code
- [ ] Secure headers

### UX/Accessibility
- [ ] Medical disclaimer
- [ ] Loading states
- [ ] Error messages
- [ ] ARIA labels
- [ ] Mobile-responsive
- [ ] Keyboard navigation

---

## 📈 SUCCESS METRICS

After refactoring, should achieve:
- ✅ **Build status**: Clean build with no warnings
- ✅ **Code coverage**: >70% test coverage
- ✅ **Performance**: <2s inference time
- ✅ **Accessibility**: WCAG AA standard
- ✅ **Mobile**: Works perfectly on mobile browsers
- ✅ **Documentation**: Every function has docstring
- ✅ **Error handling**: Graceful fallback for all failures
- ✅ **Medical compliance**: Clear disclaimer, no over-claiming

---

## 🎯 IMMEDIATE NEXT STEPS

1. **Create config management** (Python + JS)
2. **Refactor backend modules**
3. **Create React hooks**
4. **Add disclaimer & medical theme**
5. **Fix feature extraction**
6. **Add PDF export**
7. **Write documentation**
8. **Add test coverage**

---

**Status**: Ready to begin Phase 1 execution
**Estimated Time**: 6-8 hours for complete refactor
**Risk**: Medium (requires careful feature validation)

