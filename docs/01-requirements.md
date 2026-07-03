# Marlish.AI — Requirements Specification

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Production (NLLB-200 + Transliteration Pipeline)
>
> **REVISION NOTE:** Revised from the hybrid 8-layer NLP rule engine + IndicTrans2 architecture to a pure ML pipeline using Meta's NLLB-200-1.3B model with custom transliteration preprocessing. The rule-based dictionary engine has been fully replaced by neural machine translation.

---

## 1. Product Overview

Marlish.AI is a real-time translation engine for Indian chat languages. It handles:
- **Marlish** (romanized Marathi typed in Latin script)
- **Hinglish** (romanized Hindi typed in Latin script)
- **Pure Marathi/Hindi** (Devanagari script)
- **English**

All 8 translation directions are supported between these 5 language codes.

## 2. Functional Requirements

### 2.1 Translation
- **FR-1:** Accept text in any of the 5 supported languages and translate to any other.
- **FR-2:** Automatically transliterate romanized input (Marlish/Hinglish) to Devanagari before translation.
- **FR-3:** Optionally apply grammar/fluency correction (GEC) to English output.
- **FR-4:** Return translation results with latency metadata.
- **FR-5:** Support reverse transliteration (Devanagari → romanized) for Marlish/Hinglish output.

### 2.2 User Interface
- **FR-6:** Real-time translation as the user types (adaptive debounce: 300-800ms).
- **FR-7:** Language selector with swap button for quick direction changes.
- **FR-8:** Translation history stored locally (localStorage).
- **FR-9:** Copy-to-clipboard for translation output.
- **FR-10:** Dark mode, responsive design (mobile + desktop).

### 2.3 API
- **FR-11:** REST API with `POST /translate` and `GET /health` endpoints.
- **FR-12:** CORS support for cross-origin frontend requests.
- **FR-13:** Graceful error handling and fallback when GEC is unavailable.

## 3. Non-Functional Requirements

### 3.1 Performance
- **NFR-1:** Translation latency < 3s on GPU, < 30s on CPU.
- **NFR-2:** Frontend first paint < 2s.
- **NFR-3:** Model loads once at startup; subsequent requests use cached model.

### 3.2 Scalability
- **NFR-4:** Stateless API — can scale horizontally with multiple instances.
- **NFR-5:** Model weights cached on disk (~2.5GB) after first download.

### 3.3 Cost
- **NFR-6:** Free tier deployment (HF Spaces CPU + Vercel).
- **NFR-7:** Optional paid GPU upgrade for production speed.
- **NFR-8:** Gemini GEC uses free tier (15 RPM, 1M tokens/day).

### 3.4 Security
- **NFR-9:** API keys stored in `.local.env` (not committed to git).
- **NFR-10:** CORS restricted to known frontend domains.
- **NFR-11:** No user data stored server-side.

## 4. Supported Language Pairs

| Source | Target | Method |
|--------|--------|--------|
| Marathi (Devanagari) | English | NLLB direct |
| Hindi (Devanagari) | English | NLLB direct |
| Marlish (romanized) | English | Transliterate → NLLB |
| Hinglish (romanized) | English | Transliterate → NLLB |
| English | Marathi | NLLB direct |
| English | Hindi | NLLB direct |
| English | Marlish | NLLB → reverse transliterate |
| English | Hinglish | NLLB → reverse transliterate |

## 5. Quality Targets

Based on Carnival Tours test (104 segments, June 2026):
- Pure Devanagari ↔ English: **11-13/13 segments** convey correct meaning
- Romanized ↔ English: **10-11/13 segments** convey correct meaning
- Acceptable: spelling/wording variations as long as meaning is preserved
