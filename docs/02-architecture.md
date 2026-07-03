# Marlish.AI — System Architecture

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Production
>
> **REVISION NOTE:** Architecture fully migrated from offline-first rule-based NLP engine to a server-side ML translation pipeline using NLLB-200-1.3B.

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                      │
│                                                         │
│   Next.js 16 + React 19 + Tailwind CSS v4              │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │ Translator  │  │  Language    │  │  Action Bar  │  │
│   │ Panel       │  │  Selector   │  │  (History)   │  │
│   └──────┬──────┘  └──────────────┘  └──────────────┘  │
│          │ useTranslation() hook                        │
│          │ Adaptive debounce (300-800ms)                │
└──────────┼──────────────────────────────────────────────┘
           │ HTTPS POST /translate
           │ JSON { text, source, target }
           ▼
┌─────────────────────────────────────────────────────────┐
│                    API SERVER                            │
│              FastAPI + Uvicorn (Port 8000/7860)          │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │  1. INPUT CLASSIFICATION                        │   │
│   │     Token classifier: English vs Marlish/Hindi  │   │
│   └─────────────────────┬───────────────────────────┘   │
│                         ▼                               │
│   ┌─────────────────────────────────────────────────┐   │
│   │  2. TRANSLITERATION PIPELINE (for romanized)    │   │
│   │     Tier 1: IndicXlit (AI, if available)        │   │
│   │     Tier 2: Seed Map (400+ words, O(1) lookup)  │   │
│   │     Tier 3: Phoneme Rules (character-level)     │   │
│   └─────────────────────┬───────────────────────────┘   │
│                         ▼                               │
│   ┌─────────────────────────────────────────────────┐   │
│   │  3. NLLB-200-1.3B TRANSLATION                   │   │
│   │     Meta's multilingual NMT (200 languages)     │   │
│   │     mar_Deva/hin_Deva ↔ eng_Latn               │   │
│   └─────────────────────┬───────────────────────────┘   │
│                         ▼                               │
│   ┌─────────────────────────────────────────────────┐   │
│   │  4. POST-PROCESSING                             │   │
│   │     • Gemini GEC (English output only, optional)│   │
│   │     • Reverse transliteration (Marlish/Hinglish)│   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 2. Component Details

### 2.1 Frontend (Next.js on Vercel)
- **Framework:** Next.js 16 with App Router
- **UI:** React 19 components with Tailwind CSS v4
- **State:** Local (useState + localStorage for history)
- **API Communication:** `useTranslation` hook with AbortController, adaptive debounce
- **Deployment:** Vercel free tier (bom1 region — Mumbai)

### 2.2 API Server (FastAPI on HF Spaces)
- **Framework:** FastAPI with CORSMiddleware
- **Deployment:** HF Spaces Docker (free tier CPU / optional T4 GPU)
- **Port:** 7860 (HF Spaces) / 8000 (local dev)
- **Endpoints:**
  - `POST /translate` — main translation
  - `GET /health` — liveness + model status

### 2.3 Transliteration Pipeline
Converts romanized chat text (Marlish/Hinglish) to proper Devanagari before NLLB translation.

| Tier | Method | Accuracy | Speed |
|------|--------|----------|-------|
| 1 | IndicXlit (AI) | Highest | Moderate |
| 2 | Seed Map (400+ words) | High for known words | O(1) |
| 3 | Phoneme Rules | Reasonable | O(n) |

**Key files:**
- `scripts/transliterator/pipeline.py` — orchestrator
- `scripts/transliterator/fallback_map.py` — seed map with 400+ entries
- `scripts/transliterator/phoneme_rules.py` — character-level with conjunct consonant support
- `scripts/transliterator/token_classifier.py` — English vs Marlish detection
- `scripts/transliterator/reverse_transliterate.py` — Devanagari → romanized output

### 2.4 Translation Model (NLLB-200-1.3B)
- **Model:** `facebook/nllb-200-1.3B` (Meta)
- **Parameters:** 1.3 billion
- **Languages:** 200 (we use: eng_Latn, mar_Deva, hin_Deva)
- **Size:** ~2.5GB on disk
- **Inference:** GPU (1-2s) or CPU (15-30s)
- **Loading:** Once at startup, cached in memory

### 2.5 Gemini GEC (Optional)
- **Model:** `gemini-2.5-flash-lite` via `google-genai` SDK
- **Purpose:** Polish English output grammar and fluency
- **Trigger:** Only for English target, only if API key is set
- **Fallback:** Raw NLLB output if Gemini unavailable
- **Cost:** Free tier (15 requests/min, 1M tokens/day)

## 3. Data Flow

### Marlish → English
```
"kasa ahes mitra"
  → Token Classifier: [MARLISH, MARLISH, MARLISH]
  → Seed Map: "कसा" "आहेस" "मित्र"
  → NLLB: "How are you, friend?"
  → Gemini GEC: "How are you, friend?" (no change needed)
```

### English → Marlish
```
"How are you?"
  → NLLB: "तू कसा आहेस?"
  → Reverse Transliterate: "tu kasa ahes?"
```

## 4. Deployment

| Component | Platform | Tier | Cost |
|-----------|----------|------|------|
| Frontend | Vercel | Free | ₹0 |
| API | HF Spaces Docker | Free (CPU) | ₹0 |
| GEC | Gemini API | Free | ₹0 |
| Domain | Optional | Paid | ~₹800/yr (.in) |
