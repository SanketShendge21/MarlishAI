# Marlish.AI — Deployment Guide

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Production

---

## 1. Architecture Overview

| Component | Platform | Tier | Cost |
|-----------|----------|------|------|
| Frontend (Next.js) | Vercel | Free | ₹0/month |
| API Backend (FastAPI + NLLB) | HF Spaces Docker | Free (CPU) | ₹0/month |
| GEC (Gemini) | Google AI API | Free | ₹0/month |
| Domain (optional) | Namecheap/GoDaddy | Paid | ~₹800/yr (.in) |

## 2. Frontend Deployment (Vercel)

### 2.1 Setup
1. Push code to GitHub
2. Connect repo to Vercel (https://vercel.com)
3. Vercel auto-detects Next.js and deploys

### 2.2 Configuration
**`vercel.json`:**
```json
{
  "framework": "nextjs",
  "regions": ["bom1"],
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "https://your-space.hf.space"
    }
  }
}
```

### 2.3 Environment Variables
| Variable | Where | Value |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | Vercel build env | HF Spaces URL |

### 2.4 Custom Domain (Optional)
1. Buy domain (e.g., `marlishai.in` — ~₹800/yr)
2. In Vercel: Settings → Domains → Add domain
3. Update DNS records as Vercel instructs
4. SSL is automatic

## 3. API Deployment (HF Spaces)

### 3.1 Create Space
1. Go to https://huggingface.co/spaces
2. Create new Space with:
   - **SDK:** Docker
   - **Hardware:** CPU basic (free) — upgrade to T4 GPU for speed
3. The Space uses `Dockerfile` and `requirements-api.txt` from the repo

### 3.2 Push API Code
```bash
# Clone the HF Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/marlishai-api hf-deploy

# Copy required files
cp Dockerfile hf-deploy/
cp requirements-api.txt hf-deploy/
cp README_HF.md hf-deploy/README.md
cp -r api/ hf-deploy/api/
cp -r scripts/transliterator/ hf-deploy/scripts/transliterator/

# Push
cd hf-deploy
git add .
git commit -m "Deploy MarlishAI API"
git push
```

### 3.3 Secrets
In HF Space Settings → Secrets:
| Secret Name | Value |
|-------------|-------|
| `Marlish_Gemini_API_Key` | Your Gemini API key |

### 3.4 What Gets Deployed
Only these files are in the Docker image:
- `api/app.py` — FastAPI server
- `scripts/transliterator/` — transliteration pipeline
- NLLB-200-1.3B downloads automatically on first start (~2.5GB)

## 4. Local Development

### 4.1 Frontend
```bash
npm install
npm run dev
# Open http://localhost:3000
```

### 4.2 API Backend
```bash
python -m venv venv
.\venv\Scripts\activate          # Windows
pip install torch --index-url https://download.pytorch.org/whl/cu124  # GPU
pip install -r requirements-api.txt

# Create .local.env with: Marlish_Gemini_API_Key=your_key
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

## 5. Performance by Tier

| Hardware | Latency | Cost | Use Case |
|----------|---------|------|----------|
| CPU (HF free) | 15-30s/request | ₹0 | Demo, testing |
| T4 GPU (HF paid) | 1-2s/request | ~₹50/hr | Production |
| RTX 4050 (local) | 1-2s/request | ₹0 (your hardware) | Development |

## 6. Monitoring

### Health Check
```bash
curl https://your-space.hf.space/health
```
Response:
```json
{
  "status": "ok",
  "model": "facebook/nllb-200-1.3B",
  "device": "cpu",
  "ready": true,
  "gec_enabled": true
}
```

### HF Spaces Logs
- View in HF Space → Logs tab
- Watch for `[Startup] API ready.` message
- Model download takes ~5 min on first deploy
