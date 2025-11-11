# 🚀 Deployment Guide - ParkiSense

Complete guide for deploying ParkiSense to production using Vercel and external backend hosting.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│         Frontend (React/Vite) - Vercel              │
│  - Static site with client-side audio recording     │
│  - Built with npm run build                         │
│  - Deployed to Vercel CDN                           │
└────────────────────┬────────────────────────────────┘
                     │ API calls (HTTPS)
                     ▼
┌─────────────────────────────────────────────────────┐
│        Backend (FastAPI) - Separate Service         │
│  - Python ML inference server                       │
│  - Deployed to Railway, Heroku, or similar          │
│  - Scaled for audio processing                      │
└─────────────────────────────────────────────────────┘
```

## Part 1: Prepare Frontend for Deployment

### 1.1 Environment Configuration

**Create `.env.production` in project root:**

```bash
VITE_API_URL=https://your-backend-domain.com
VITE_ENV=production
VITE_ENABLE_DEBUG=false
VITE_ENABLE_LOCAL_MODEL=false
```

Replace `your-backend-domain.com` with your actual backend URL.

### 1.2 Test Build Locally

```bash
# Install dependencies
npm install

# Build frontend
npm run build

# Preview production build locally
npm run preview
```

### 1.3 Verify Configuration

```bash
# Lint and validate
npm run lint
npm run validate
```

## Part 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account

1. Go to https://vercel.com
2. Sign up with GitHub
3. Connect your GitHub repository

### 2.2 Configure Project

**In Vercel Dashboard:**

1. Import the repository
2. Framework: **Vite**
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Environment Variables:

   ```
   VITE_API_URL = https://your-backend-domain.com
   VITE_ENV = production
   VITE_ENABLE_DEBUG = false
   ```

6. Click **Deploy**

### 2.3 Post-Deployment

- Verify the site loads at `https://your-project.vercel.app`
- Test audio recording works
- Check console for any errors
- Verify API calls in Network tab point to correct backend URL

## Part 3: Deploy Backend Separately

The backend cannot run on Vercel's free tier (it requires persistent Python environment and model storage). Use an alternative:

### Option A: Railway (Recommended)

**Fastest setup:**

1. Go to https://railway.app
2. Create new project
3. Connect GitHub repository
4. Select the root directory (or specify `ml/` if needed)
5. Add environment variables:

   ```
   ENVIRONMENT=production
   DEBUG=false
   PD_MODEL_PATH=ml/models/best_pd_model.pkl
   ALLOWED_ORIGINS=https://your-project.vercel.app
   ```

6. Railway auto-deploys on push

### Option B: Heroku (Alternative)

1. Create `Procfile` in root:

   ```
   web: cd ml && uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```

2. Deploy:

   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Option C: Docker + Any Cloud

1. Create `Dockerfile` in root:

   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   
   COPY ml/requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY ml/ ./ml/
   COPY utils/ ./utils/
   
   CMD ["uvicorn", "ml.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Build and push to Docker Hub, then deploy to any cloud platform

## Part 4: Model File Management

### Critical: Models Are Large

The ML model file (`ml/models/best_pd_model.pkl`) can be >100MB. **Don't commit to Git!**

### Solution: Download at Runtime

Update `ml/config.py`:

```python
import os
from pathlib import Path

MODEL_PATH = Path(os.getenv('PD_MODEL_PATH', 'ml/models/best_pd_model.pkl'))

def ensure_model_exists():
    """Download model from cloud storage if missing."""
    if not MODEL_PATH.exists():
        # Example: download from AWS S3, Google Cloud Storage, etc.
        import requests
        model_url = os.getenv('MODEL_DOWNLOAD_URL')
        if model_url:
            print(f"Downloading model from {model_url}...")
            response = requests.get(model_url)
            MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(MODEL_PATH, 'wb') as f:
                f.write(response.content)
```

### Alternative: Use versioned model storage

1. Store model in AWS S3, Google Cloud Storage, or similar
2. On backend startup, download model
3. Set `MODEL_DOWNLOAD_URL` environment variable

## Part 5: Final Verification Checklist

### Frontend (Vercel)

- [ ] Site loads at production URL
- [ ] No console errors
- [ ] Responsive design works on mobile
- [ ] Audio recording functions
- [ ] Results display correctly
- [ ] PDF export works
- [ ] All UI elements render

### Backend Connectivity

- [ ] `/health` endpoint responds
- [ ] `/info` endpoint returns model info
- [ ] `/predict` endpoint accepts audio files
- [ ] CORS headers correct (allows frontend domain)
- [ ] Error responses are graceful

### Security

- [ ] No API keys in frontend code
- [ ] `.env` files not committed
- [ ] HTTPS enforced on both frontend and backend
- [ ] CORS properly scoped (not `*`)
- [ ] Security headers set (X-Content-Type-Options, etc.)

### Performance

- [ ] Frontend builds in <60 seconds
- [ ] Home page loads in <3 seconds
- [ ] Audio upload takes <10 seconds
- [ ] Results display within 5 seconds

## Part 6: Continuous Deployment

### Enable Auto-Deploy

**Vercel:** Automatically deploys on push to main branch

**Railway/Heroku:** Configure GitHub integration for auto-deploy

### Monitor Deployments

**Vercel Analytics:**
- Go to project → Analytics
- Monitor FCP, LCP, CLS

**Backend Logs:**
- Railway: Deployments → Logs
- Heroku: `heroku logs --tail`

## Part 7: Environment Variables Quick Reference

### Frontend (`VITE_*` prefix)

| Variable | Default | Production |
|----------|---------|-----------|
| `VITE_API_URL` | `http://127.0.0.1:8000` | `https://your-backend.com` |
| `VITE_ENV` | `development` | `production` |
| `VITE_ENABLE_DEBUG` | `true` | `false` |

### Backend

| Variable | Default | Production |
|----------|---------|-----------|
| `ENVIRONMENT` | `development` | `production` |
| `DEBUG` | `true` | `false` |
| `ALLOWED_ORIGINS` | `*` | `https://your-domain.com` |
| `PD_MODEL_PATH` | `ml/models/best_pd_model.pkl` | Cloud URL or path |

## Part 8: Troubleshooting

### "API requests failing" (CORS error)

**Solution:** Update backend `ALLOWED_ORIGINS` to include your Vercel domain

```
ALLOWED_ORIGINS=https://your-project.vercel.app,https://www.your-project.vercel.app
```

### "Model not found" on backend

**Solution:** Ensure `PD_MODEL_PATH` points to correct location or implement model download function

### "Build fails on Vercel"

**Solution:** Check build logs, verify `package.json` has all dependencies:

```bash
npm install
npm run build
```

### "Slow prediction time"

**Solution:** 
- Ensure backend has sufficient resources
- Consider GPU acceleration for ML inference
- Implement result caching for identical inputs

## Part 9: Next Steps

- [ ] Set up monitoring and alerts
- [ ] Configure custom domain
- [ ] Set up email notifications for errors
- [ ] Document API for users
- [ ] Add analytics
- [ ] Plan scaling strategy

---

**Last Updated:** November 11, 2025  
**Version:** 1.0
