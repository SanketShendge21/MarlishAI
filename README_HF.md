---
title: MarlishAI Translation API
emoji: 🌐
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
suggested_hardware: t4-small
pinned: true
license: mit
---

# MarlishAI Translation API

Real-time translation API for Marathi, Hindi, Marlish (romanized Marathi), Hinglish (romanized Hindi) ↔ English.

## API Endpoints

### `POST /translate`
```json
{
  "text": "kasa ahes mitra",
  "source": "marlish",
  "target": "english"
}
```

### `GET /health`
Returns model status, GEC availability, and device info.

## Supported Languages
- `english` — English
- `marathi` — Marathi (Devanagari)
- `hindi` — Hindi (Devanagari)
- `marlish` — Romanized Marathi (chat-style)
- `hinglish` — Romanized Hindi (chat-style)

## Tech Stack
- **Model:** NLLB-200-1.3B (Meta)
- **Transliteration:** Custom phoneme pipeline + 400+ word seed map
- **GEC:** Gemini 2.5-flash-lite (optional post-processing for English output)
- **Runtime:** FastAPI + PyTorch (CUDA)
