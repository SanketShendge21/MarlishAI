---
title: MarlishAI Translation API
emoji: 🌐
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: true
license: mit
---

# MarlishAI Translation API

Real-time translation API for Marathi, Hindi, Marlish (romanized Marathi), Hinglish (romanized Hindi) ↔ English.

Powered by Meta's NLLB-200-1.3B model with a custom transliteration pipeline for romanized Indian languages.

## API Endpoints

### `POST /translate`
```json
{
  "text": "kasa ahes mitra",
  "source": "marlish",
  "target": "english"
}
```

**Response:**
```json
{
  "translation": "How are you, friend?",
  "source": "marlish",
  "target": "english",
  "latency_ms": 1200
}
```

### `GET /health`
Returns model status, GEC availability, and device info.

## Supported Languages
| Code | Language | Script |
|------|----------|--------|
| `english` | English | Latin |
| `marathi` | Marathi | Devanagari |
| `hindi` | Hindi | Devanagari |
| `marlish` | Romanized Marathi | Latin (chat-style) |
| `hinglish` | Romanized Hindi | Latin (chat-style) |

## Architecture
- **Translation Model:** NLLB-200-1.3B (Meta) — 200 language pairs
- **Transliteration:** Custom 3-tier pipeline (IndicXlit → 400+ word seed map → phoneme rules)
- **GEC:** Gemini 2.5-flash-lite (optional English post-processing, free tier)
- **API:** FastAPI + Uvicorn
- **Runtime:** CPU (free tier) — upgrade to GPU for faster inference
