# Marlish.AI — Requirements Specification

> **Version:** 2.0 | **Date:** 2026-04-19 | **Status:** Updated (Open-Source First)

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
| FR-01 | Real-time translation output as the user types | **P0** | 250ms debounce; client-side NLLB-200 or edge fallback |
| FR-02 | Support all 5 translation pairs listed above | **P0** | Language pair selection via dropdown |
| FR-03 | Auto-detect source language (Hinglish vs Marlish vs English) | **P1** | fastText LID (client-side, ~1MB) |
| FR-04 | Swap source and target languages with one click | **P0** | Only for valid reverse pairs |
| FR-05 | Handle code-switched input (intra-sentential mixing) | **P0** | e.g., "kal scene kya hai?" to contextual translation |
| FR-06 | Resolve Romanized spelling variations and vowel omissions | **P0** | e.g., "mzh nv" to "majha nav" to "my name" |
| FR-07 | Preserve intent over literal translation | **P0** | Slang/idiom mapping, not word-for-word |
| FR-08 | Progressive model loading with edge fallback | **P1** | NLLB-200 downloads in background; edge serves during download |

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
| FR-16 | Translation history (recent translations) | **P2** | Stored locally in IndexedDB or localStorage |
| FR-17 | PWA installable (Add to Home Screen) | **P2** | Service worker + manifest.json |

### 3.3 Performance and Reliability

| ID | Requirement | Priority | Notes |
|----|------------|----------|-------|
| FR-18 | End-to-end translation latency < 500ms | **P0** | Tier 1: < 10ms, Tier 2: 100-500ms, Tier 3: 200-800ms |
| FR-19 | Offline translation after model download | **P0** | NLLB-200 cached in IndexedDB (~150MB q4) |
| FR-20 | Graceful degradation on network failure | **P1** | Use Tier 2 (in-browser) if offline; show "Offline" badge |
| FR-21 | Local caching of translation results | **P1** | IndexedDB, 500 entries, LRU eviction, 30-day TTL |

### 3.4 Security

| ID | Requirement | Priority | Notes |
|----|------------|----------|-------|
| FR-22 | Rate limiting on edge fallback (Tier 3) | **P0** | Cloudflare Workers: 100K free/day |
| FR-23 | Prompt injection prevention (Tier 3 only) | **P1** | Sandbox user input in hard delimiters (edge prompts) |
| FR-24 | Input sanitization (XSS, script injection) | **P0** | Client-side + server-side validation |
| FR-25 | No API keys required for core translation | **P0** | Client-side models = no keys exposed |

---

## 4. Non-Functional Requirements

| Category | Requirement | Target |
|----------|------------|--------|
| **Performance** | First Contentful Paint (FCP) | < 1.2s |
| **Performance** | Time to Interactive (TTI) | < 2.0s |
| **Performance** | First Load Size (gzipped) | < 150 KB |
| **Performance** | Lighthouse Score | 95+ across all categories |
| **Scalability** | Concurrent users | 10,000+ MAU on free/hobby tier |
| **Availability** | Uptime SLA | 99.5% (Vercel + Cloudflare) |
| **Accessibility** | WCAG compliance | AA level minimum |
| **Responsiveness** | Mobile-first design | 320px to 1440px breakpoints |
| **Browser Support** | Modern browsers | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |
| **i18n** | UI language | English (expandable to Hindi/Marathi UI later) |

---

## 5. Constraints and Assumptions

### Constraints
- **Budget:** $0 — $5/month target for first 10,000 MAU (open-source stack)
- **Solo developer / small team** — architecture must minimize operational overhead
- **Indian mobile network conditions** — must perform on 3G/4G with high latency
- **Initial model download:** ~150MB NLLB-200 (q4) — must be manageable on Indian networks
- **No native app** — web-only PWA for cross-platform reach

### Assumptions
- Users primarily type on QWERTY keyboards using Roman script
- Most users access from mobile devices (Android > iOS)
- Users expect near-instant feedback (< 500ms perceived latency)
- ~60%+ of target users have WebGPU-capable browsers (Chrome 113+)
- Users on low-end devices will transparently fall back to edge (Tier 3)
- Code-mixed input follows common patterns documented in L3Cube and AI4Bharat research
- NLLB-200 distilled model is sufficient for 80%+ of common translation queries

---

## 6. Out of Scope (v1.0)

- Voice-to-voice translation (future phase)
- Camera/OCR-based translation
- Custom keyboard extension (iOS/Android)
- Multi-document upload and batch translation
- User accounts and authentication (v1 is anonymous)
- Fine-tuned custom models (Phase 3 roadmap)

---

## 7. Success Metrics

| Metric | Target (3 months post-launch) |
|--------|-------------------------------|
| Monthly Active Users (MAU) | 1,000+ |
| Average translation latency (Tier 2) | < 500ms |
| Offline translation availability | > 80% of requests handled client-side |
| User retention (Day-7) | > 30% |
| Lighthouse Performance Score | 95+ |
| Monthly infrastructure cost | < $5 at 10K MAU |
| User satisfaction (in-app feedback) | > 4.0/5.0 |
