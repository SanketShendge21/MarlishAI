# Marlish.AI — Requirements Specification

> **Version:** 3.0 | **Date:** May 2026 | **Status:** Approved (Hybrid AI/ML Architecture)
> 
> **REVISION NOTE (Strategic Pivot):** This document has been revised from scratch training a custom translation model (`google/mt5-small`) to a **three-tier hybrid architecture**. Fine-tuning `mt5-small` yielded a low BLEU score of ~3 due to noisy dataset challenges and capacity limitations. The app now routes common phrases to an in-memory 8-layer NLP Rule Engine, while complex queries are preprocessed by a custom transliteration pipeline and translated via pre-trained models (online IndicTrans2 API or offline in-browser opus-mt ONNX).

---

## 1. Product Vision

**Marlish.AI** is a lightweight, responsive, real-time web application that translates and transliterates between code-mixed Indian languages — specifically Hinglish, Marlish (Marathi typed in Roman script), English, Hindi, and Marathi. The app provides instant translation output **as the user types**, delivering a seamless, native-feeling experience optimized for Indian mobile users.

---

## 2. Supported Translation Pairs

| # | Source Language | Target Language | Direction Code | Description |
|---|----------------|-----------------|----------------|-------------|
| 1 | **Hinglish** (Hindi + English in Roman) | **English** | `HIN_EN → EN` | Romanized Hindi-English mix to formal English |
| 2 | **Hinglish** | **Marathi** (Devanagari) | `HIN_EN → MR` | Romanized Hindi-English mix to native Marathi |
| 3 | **English** | **Marathi** (Devanagari) | `EN → MR` | Standard English to native Marathi |
| 4 | **Marlish** (Marathi in Roman) | **English** | `MR_EN → EN` | Romanized Marathi to formal English |
| 5 | **Marlish** | **Hindi** (Devanagari) | `MR_EN → HI` | Romanized Marathi to native Hindi |

> **Note:**
> "Hinglish" = Hindi words typed in English script, often mixed with English words (e.g., "kal meeting hai bro").
> "Marlish" = Marathi words typed in English script (e.g., "mi ghari jato").

---

## 3. Functional Requirements

### 3.1 Core Translation Engine

| ID | Requirement | Priority | Notes |
|----|------------|----------|-------|
| FR-01 | Real-time translation output as the user types | **P0** | 250ms debounce; client-side rule-based translation + lazy-loaded ONNX fallback |
| FR-02 | Support all 5 translation pairs listed above | **P0** | Language pair selection via dropdown |
| FR-03 | Custom Transliteration Preprocessing Pipeline | **P0** | Preprocesses Romanized Hinglish/Marlish into Devanagari using a seed map, dataset-derived frequency mapping, and phoneme rule fallback before feeding the text to ML translation models. |
| FR-04 | Swap source and target languages with one click | **P0** | Only for valid reverse pairs |
| FR-05 | Handle code-switched input (intra-sentential mixing) | **P0** | e.g., "kal scene kya hai?" to contextual translation |
| FR-06 | Resolve Romanized spelling variations and vowel omissions | **P0** | e.g., "mzh nv" to "majha nav" to "my name" |
| FR-07 | Preserve intent over literal translation | **P0** | Slang/idiom mapping in rule engine, contextual NMT/LLM for complex structures |
| FR-08 | Progressive translation with dual-path edge/local ML | **P1** | Routes to hosted API (IndicTrans2) when online; transparently falls back to quantized in-browser models (opus-mt ONNX) when offline or API is down. |

### 3.2 User Interface

| ID | Requirement | Priority | Notes |
|----|------------|----------|-------|
| FR-09 | Dual-panel layout: input (top) + output (bottom) | **P0** | Mobile-first, responsive |
| FR-10 | Language selector dropdowns with swap button | **P0** | Visually prominent |
| FR-11 | Copy translated text to clipboard | **P0** | With micro-animation feedback (checkmark) |
| FR-12 | Clear input with one tap (X button) | **P0** | Appears when text is present |
| FR-13 | Dark mode / Light mode toggle | **P1** | Default to system preference |
| FR-14 | Text-to-Speech (TTS) for translated output | **P1** | Browser Web Speech API |
| FR-15 | Share to WhatsApp button | **P1** | Deep link: `https://wa.me/?text=...` |
| FR-16 | User feedback interface | **P1** | Thumbs up/down and text input for corrections to feed telemetry |
| FR-17 | PWA installable (Add to Home Screen) | **P2** | Service worker + manifest.json |

### 3.3 Performance and Reliability

| ID | Requirement | Priority | Notes |
|----|------------|----------|-------|
| FR-18 | End-to-end translation latency < 500ms on common paths | **P0** | Tier 1 (cache/rule engine): < 5ms. Tier 2 (Online API): 200-500ms. Tier 2 (Offline ONNX): 500-1500ms. |
| FR-19 | Offline translation fallback | **P0** | Local translation via 8-layer engine and cached browser-based opus-mt ONNX model (~40-75MB download, cached in IndexedDB). |
| FR-20 | Graceful degradation on network failure | **P1** | Use local ONNX model if offline; show "Offline" status badge |
| FR-21 | Local caching of translation results | **P1** | IndexedDB, 500 entries, LRU eviction, 30-day TTL |

### 3.4 Security

| ID | Requirement | Priority | Notes |
|----|------------|----------|-------|
| FR-22 | Rate limiting on hosted ML API endpoint | **P0** | Limit to 60 req/min per IP to prevent Denials of Wallet |
| FR-23 | Input sanitization (XSS, script injection) | **P0** | Client-side + server-side validation |
| FR-24 | Secure storage of API credentials | **P0** | Secrets stored securely on hosted FastAPI env (e.g. Hugging Face Spaces `HF_TOKEN`) |

---

## 4. Non-Functional Requirements

| Category | Requirement | Target |
|----------|------------|--------|
| **Performance** | First Contentful Paint (FCP) | < 1.2s |
| **Performance** | Time to Interactive (TTI) | < 2.0s |
| **Performance** | First Load Size (gzipped) | < 150 KB |
| **Performance** | Lighthouse Score | 95+ across all categories |
| **Scalability** | Concurrent users | 10,000+ MAU on free/hobby tier |
| **Availability** | Uptime SLA | 99.5% (Vercel + Hosted API Spaces) |
| **Accessibility** | WCAG compliance | AA level minimum |
| **Responsiveness** | Mobile-first design | 320px to 1440px breakpoints |
| **Browser Support** | Modern browsers | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |
| **i18n** | UI language | English (expandable to Hindi/Marathi UI later) |

---

## 5. Constraints and Assumptions

### Constraints
- **Budget:** $0 — $5/month target for first 10,000 MAU (open-source stack)
- **Indian mobile network conditions** — must perform on 3G/4G with high latency (mitigated by < 5ms local Tier 1 engine handling ~80% of inputs)
- **Browser model size limit:** Offline fallback model must be compressed to < 75MB (achieved using quantized `opus-mt-mr-en` ONNX)
- **No native app** — web-only PWA for cross-platform reach

### Assumptions
- Users primarily type on QWERTY keyboards using Roman script
- Most users access from mobile devices (Android > iOS)
- Users expect near-instant feedback (< 500ms perceived latency for standard chat)
- Users on low-end devices or offline will transparently fall back to cached local models
- Code-mixed input follows common patterns documented in L3Cube and AI4Bharat research

---

## 6. Out of Scope (v1.0)

- Voice-to-voice translation (future phase)
- Camera/OCR-based translation
- Custom keyboard extension (iOS/Android)
- Multi-document upload and batch translation
- Fine-tuned seq2seq custom models trained from scratch (superseded by pre-trained hybrid model pivot)

---

## 7. Success Metrics

| Metric | Target (3 months post-launch) |
|--------|-------------------------------|
| Monthly Active Users (MAU) | 1,000+ |
| Average translation latency (Tier 1) | < 5ms |
| Offline translation availability | > 80% of requests handled client-side |
| User retention (Day-7) | > 30% |
| Monthly infrastructure cost | < $5 at 10K MAU |
| Retrained model corpus | 10,000+ user-corrected gold sentence pairs logged via Kafka |
