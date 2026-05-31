# Phase 4: Pure ML Translation API — Implementation Plan

**Date:** May 30, 2026  
**Status:** In Progress  
**Supersedes:** The hybrid tier-router architecture in `ARCHITECTURE_ANALYSIS_AND_PLAN.md` (Sections 6–7)

---

## Architecture Decision

The 8-layer rule engine, offline ONNX path, and tier-routing system are **no longer part of the translation pipeline**. The application is a standard online service:

```
User types Marlish → Website (Next.js) → POST /translate → Backend API (FastAPI)
                                                              │
                                                    1. Transliterate (Marlish → Devanagari)
                                                       Using Phase 2 pipeline (100% accuracy)
                                                    2. NLLB-200 inference (Devanagari → English)
                                                       BLEU 40.71 (Phase 3 benchmark)
                                                              │
                                              ← JSON response ← { translation, devanagari, latency_ms }
```

**Why this change:**
- The 8-layer rule engine is not needed — pure ML translation via NLLB-200 handles everything
- NLLB-200 (600M params, ~2.4GB) is too large for browser ONNX — must be server-side
- The app will always require internet — no offline mode
- This matches how standard LLM/translation services work

---

## Hosting Plan

| Component | Platform | Cost |
|-----------|----------|------|
| Frontend (Next.js) | Vercel | Free |
| Backend API (FastAPI + NLLB-200) | Hugging Face Spaces | Free (16GB RAM CPU, or free T4 GPU grant) |

---

## Files Created

### `api/app.py` — FastAPI Translation Server
- **Endpoint:** `POST /translate` — accepts `{ text }`, returns `{ translation, devanagari, latency_ms }`
- **Endpoint:** `GET /health` — liveness check with model status
- **On startup:** Loads NLLB-200 (FP16 on GPU, FP32 on CPU) + transliteration pipeline
- **CORS:** Enabled for all origins (tighten in production)
- **Dependencies:** `fastapi`, `uvicorn`, `torch`, `transformers`, `sentencepiece`

### `api/requirements.txt` — API-specific dependencies

---

## What Still Needs to Be Done

### 1. Test API Server Locally
```bash
# Start the server
uvicorn api.app:app --host 0.0.0.0 --port 8000

# Test with curl (PowerShell)
$body = '{"text": "kasa ahes mitra"}'
Invoke-RestMethod -Uri http://localhost:8000/translate -Method POST -Body $body -ContentType "application/json"

# Expected response:
# { "translation": "How are you, friend?", "devanagari": "कसा आहेस मित्र", "latency_ms": ... }
```

### 2. Wire Frontend to API
- Replace the current rule-engine translation call in the Next.js app with a `fetch()` to `/translate`
- Need to identify the exact component/hook that currently handles translation
- Add loading state and error handling for API calls

### 3. Deploy API to Hugging Face Spaces
- Create a new Space with Docker SDK
- Upload `api/app.py`, `api/requirements.txt`, and `scripts/transliterator/` module
- Configure the Space to run uvicorn
- API endpoint: `https://YOUR_USERNAME-marlish-api.hf.space/translate`

### 4. Deploy Frontend to Vercel
- Configure the API endpoint URL as an environment variable
- Deploy the Next.js app

---

## Files NOT Changed (preserved for portfolio)

The following files are no longer used for translation but represent real engineering work:

| File | Why it's kept |
|------|--------------|
| `lib/dictionary-engine.js` | 8-layer NLP engine — portfolio evidence |
| `lib/tier-router.js` | Tier routing logic — portfolio evidence |
| `lib/scoring-engine.js` | Confidence scoring — portfolio evidence |
| `lib/contextual-disambiguation.js` | Context analysis — portfolio evidence |
| `lib/grammar-rules.js` | SOV→SVO reordering — portfolio evidence |
| `lib/phrase-intent-rules.js` | Intent matching — portfolio evidence |
| `lib/typo-map.js` | Typo normalization — portfolio evidence |
