# Marlish.AI — Vision, Goals & Roadmap

> **Version:** 7.0 | **Date:** June 2026 | **Status:** Production (v1.0)

---

## Vision

Build an AI translation engine that understands how Indians actually communicate online — handling romanized scripts (Marlish, Hinglish), code-mixed text, and informal chat language that mainstream translators fail on.

## Current State (v1.0 — June 2026)

### What Works
- ✅ 5 languages: English, Marathi, Hindi, Marlish, Hinglish
- ✅ 8 translation directions (all pairs)
- ✅ NLLB-200-1.3B neural translation (Meta)
- ✅ Custom transliteration pipeline (400+ word seed map + phoneme rules)
- ✅ Gemini GEC for English output polishing
- ✅ Real-time UI with adaptive debounce
- ✅ Translation quality: 10-13/13 segments across all directions

### Architecture Evolution
| Phase | What | Status |
|-------|------|--------|
| v0.1 | Rule-based 8-layer NLP engine (dictionary) | ❌ Replaced |
| v0.2 | Hybrid: rules + IndicTrans2 API | ❌ Replaced (fairseq issues) |
| v0.3 | NLLB-200-600M + transliteration | ✅ Tested, superseded |
| **v1.0** | **NLLB-200-1.3B + translit + Gemini GEC** | **✅ Current** |

## Roadmap

### Phase 1: Launch (Current) ✅
- [x] NLLB-200-1.3B integration
- [x] Custom transliteration pipeline
- [x] Gemini GEC post-processing
- [x] Real-world quality testing (Carnival Tours — 104 segments)
- [x] Deployment configs (Dockerfile, Vercel, HF Spaces)
- [ ] Deploy to HF Spaces (free tier CPU)
- [ ] Deploy frontend to Vercel

### Phase 2: Quality (Post-Launch)
- [ ] QLoRA fine-tuning on curated Marlish/Hinglish pairs
- [ ] Integrate IndicXlit for AI-powered transliteration (Tier 1)
- [ ] Expand seed map to 1000+ words
- [ ] Add Kannada, Telugu support (NLLB already supports them)

### Phase 3: Scale
- [ ] Upgrade to T4 GPU on HF Spaces (1-2s latency)
- [ ] Add request caching (Redis/Vercel KV)
- [ ] Custom domain (marlishai.in)
- [ ] PWA support for mobile installation
- [ ] Translation history sync (optional account system)

### Phase 4: Advanced
- [ ] Speech-to-text input (Whisper)
- [ ] Text-to-speech output (Indic TTS)
- [ ] Document translation (PDF/image OCR → translate)
- [ ] Browser extension for inline translation
- [ ] API for third-party integrations

## Non-Goals (Intentional)
- Not building a general-purpose translator (Google Translate already exists)
- Not targeting formal/literary translation — focusing on **chat language**
- Not building native mobile apps — PWA is sufficient
- Not storing user data server-side — privacy first
