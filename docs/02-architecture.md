# Marlish.AI — System Architecture

> **Version:** 2.0 | **Date:** 2026-04-19 | **Status:** Updated (Open-Source First)
>
> **REVISION NOTE:** Architecture revised from Cloud API-dependent to a
> three-tier client-side-first approach using open-source models.
> See [08-tech-stack.md](file:///d:/Learning-Tutorials/Apni%20Bhasha/docs/08-tech-stack.md) for detailed technology choices.

---

## 1. Architecture Overview

Marlish.AI follows a **Three-Tier Hybrid** architecture — client-side inference handles the majority of requests at zero cost, with an edge/server fallback for complex cases.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           USER'S BROWSER                                 │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────────────────┐  │
│  │  Input Panel  │───▶│  Debounce    │───▶│  Translation Router        │  │
│  │  (textarea)   │    │  (250ms)     │    │  (selects Tier 1/2/3)      │  │
│  └──────────────┘    └──────────────┘    └─────┬──────┬──────┬────────┘  │
│                                                │      │      │           │
│                    ┌───────────────────────────▼┐     │      │           │
│                    │  TIER 1: INSTANT            │     │      │           │
│                    │  Aksharamukha.js (< 1MB)    │     │      │           │
│                    │  ─ Transliteration           │     │      │           │
│                    │  fastText LID (~1MB)         │     │      │           │
│                    │  ─ Language detection         │     │      │           │
│                    │  IndexedDB local cache        │     │      │           │
│                    │  ─ Previously seen phrases     │     │      │           │
│                    │                               │     │      │           │
│                    │  Latency: < 10ms | Cost: $0   │     │      │           │
│                    └───────────────────────────────┘     │      │           │
│                                                         │      │           │
│                    ┌────────────────────────────────────▼┐     │           │
│                    │  TIER 2: IN-BROWSER ML               │     │           │
│                    │  Transformers.js v4 + WebGPU         │     │           │
│                    │  NLLB-200 (Distilled 600M, q4)       │     │           │
│                    │  ─ Full sentence translation          │     │           │
│                    │  ─ Cached in IndexedDB (~150MB)       │     │           │
│                    │  ─ WebGPU accelerated (64x over WASM) │     │           │
│                    │                                       │     │           │
│                    │  Latency: 100-500ms | Cost: $0        │     │           │
│                    └───────────────────────────────────────┘     │           │
│                                                                  │           │
│  ┌──────────────────────────────────────────────────────────┐    │           │
│  │              Output Panel (translated text)               │    │           │
│  │              + Copy / TTS / Share buttons                 │    │           │
│  └──────────────────────────────────────────────────────────┘    │           │
└──────────────────────────────────────────────────────────────────┼───────────┘
                                                                   │
                              HTTPS (only when Tier 3 needed)      │
                                                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    TIER 3: EDGE / SERVER FALLBACK                         │
│                                                                          │
│  ┌─────────────────────────────┐    ┌──────────────────────────────────┐ │
│  │  Cloudflare Worker           │───▶│  Supabase Edge Function          │ │
│  │  ─ Rate limiting (100K/day)  │    │  ─ IndicTrans3 (AI4Bharat)      │ │
│  │  ─ Bot protection            │    │  ─ Gemma 3 4B (code-mixed)      │ │
│  │  ─ Request routing           │    │  ─ Indic-Xlit (transliteration) │ │
│  └─────────────────────────────┘    └──────────────────────────────────┘ │
│                                                                          │
│  Latency: 200-800ms | Cost: $0-5/month (within free tiers)              │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Pattern: Three-Tier Hybrid

### Why This Pattern?

| Approach | Assessment |
|----------|-----------|
| **Fully Client-Side** (Transformers.js only) | Great for desktop, but ~150MB initial download. WebGPU fragmented on mobile. Need edge fallback. |
| **Fully Cloud API** (Gemini / GPT) | Works but creates recurring cost ($18-108/month) and vendor lock-in. No offline. No privacy. |
| **Monolithic Backend** (FastAPI + GPU) | High server costs, cold starts, geographic latency. Overkill. |
| **Three-Tier Hybrid** ✅ | Client-side for 80%+ of requests ($0). Edge fallback for complex cases. Best of all worlds. |

### Key Design Decisions

1. **Client-side first** — Aksharamukha.js + NLLB-200 handle most translations at zero cost and zero latency
2. **Progressive model loading** — User can translate immediately via edge while NLLB-200 downloads in background
3. **WebGPU with WASM fallback** — Use GPU where available, fall back to CPU-based WASM on older devices
4. **Edge fallback, not edge primary** — Cloudflare Workers + Supabase only handle what the browser can't
5. **250ms debounce** — Same debounce strategy, but now the request often stays entirely in-browser

---

## 3. Component Architecture

### 3.1 Frontend (Next.js 16 App Router)

```
app/
├── layout.js                 # Root layout + theme provider + fonts
├── page.js                   # Main translator page (SSR shell via PPR)
├── globals.css               # Design tokens + Tailwind directives
├── not-found.js              # Custom 404 page
│
├── components/
│   ├── translator/
│   │   ├── TranslatorPanel.jsx    # Main two-panel translator
│   │   ├── InputArea.jsx          # Auto-focusing textarea with clear btn
│   │   ├── OutputArea.jsx         # Translation output + loading state
│   │   ├── LanguageSelector.jsx   # Source/Target language dropdowns
│   │   └── SwapButton.jsx         # Animated swap toggle
│   │
│   ├── actions/
│   │   ├── ActionBar.jsx          # Copy / TTS / Share / History buttons
│   │   ├── CopyButton.jsx         # Copy with checkmark animation
│   │   ├── TTSButton.jsx          # Text-to-Speech trigger
│   │   ├── ShareButton.jsx        # WhatsApp share deep link
│   │   └── HistoryDrawer.jsx      # Recent translations drawer
│   │
│   ├── ai/
│   │   ├── ModelLoader.jsx        # NLLB-200 download progress UI
│   │   └── TierIndicator.jsx      # Shows which tier is active (local/edge)
│   │
│   └── ui/
│       ├── ThemeToggle.jsx        # Dark/Light mode switch
│       ├── Header.jsx             # App header: logo + theme toggle
│       ├── Footer.jsx             # Minimal footer
│       ├── LoadingSkeleton.jsx    # Shimmer loading animation
│       └── Toast.jsx              # Toast notification component
│
├── hooks/
│   ├── useTranslation.js         # Core hook: tier routing + debounce + abort
│   ├── useModelLoader.js         # NLLB-200 loading + progress + caching
│   ├── useTransliterate.js       # Aksharamukha.js wrapper
│   ├── useDebounce.js            # Generic debounce hook
│   ├── useTheme.js               # Theme detection + toggle
│   ├── useClipboard.js           # Clipboard API wrapper
│   └── useTTS.js                 # Web Speech API wrapper
│
├── lib/
│   ├── tier-router.js            # Decides Tier 1/2/3 based on input + device
│   ├── aksharamukha.js           # Aksharamukha.js transliteration wrapper
│   ├── nllb-pipeline.js          # Transformers.js NLLB-200 pipeline setup
│   ├── language-detect.js        # fastText LID integration
│   ├── languages.js              # Language config + valid pair mappings
│   ├── constants.js              # DEBOUNCE_MS, MAX_INPUT_LENGTH, etc.
│   ├── local-cache.js            # IndexedDB cache for translations
│   ├── sanitize.js               # Input sanitization utilities
│   └── analytics.js              # PostHog event tracking
│
├── workers/
│   └── nllb-worker.js            # Web Worker for NLLB-200 inference
│                                  # (keeps UI thread responsive)
│
└── api/
    └── translate/
        └── route.js              # Edge API route (Tier 3 fallback only)
                                   #   - Validate + sanitize
                                   #   - Rate limit check
                                   #   - Route to IndicTrans3 / Gemma 3
                                   #   - Stream response back
```

### 3.2 Translation Router (Core Logic)

The Translation Router is the brain that decides which tier handles each request:

```javascript
// lib/tier-router.js

export async function routeTranslation(input, source, target, context) {
  const { webgpuAvailable, modelLoaded, isOnline } = context;

  // TIER 1: Check local cache first (always)
  const cached = await localCache.get(input, source, target);
  if (cached) {
    return { tier: 1, result: cached, source: 'cache' };
  }

  // TIER 1: Pure transliteration (Roman ↔ Devanagari only)
  if (isTransliterationPair(source, target)) {
    const result = aksharamukha.transliterate(input, source, target);
    return { tier: 1, result, source: 'aksharamukha' };
  }

  // TIER 2: In-browser NLLB-200 (if available)
  if (modelLoaded && (webgpuAvailable || wasmAvailable)) {
    try {
      const result = await nllbPipeline.translate(input, source, target);
      await localCache.set(input, source, target, result);  // cache it
      return { tier: 2, result, source: 'nllb-200' };
    } catch (err) {
      console.warn('Tier 2 failed, falling back to Tier 3:', err);
    }
  }

  // TIER 3: Edge/Server fallback
  if (isOnline) {
    const result = await fetchEdgeTranslation(input, source, target);
    await localCache.set(input, source, target, result);
    return { tier: 3, result, source: 'edge' };
  }

  // Offline and no model — show error
  return { tier: 0, result: null, source: 'offline' };
}
```

### 3.3 Web Worker for NLLB-200

Running ML inference on the main thread would freeze the UI. The NLLB-200 model runs in a **Web Worker**:

```javascript
// workers/nllb-worker.js
import { pipeline } from '@xenova/transformers';

let translator = null;

self.onmessage = async (event) => {
  const { type, text, sourceLang, targetLang } = event.data;

  if (type === 'load') {
    translator = await pipeline('translation', 'Xenova/nllb-200-distilled-600M', {
      device: 'webgpu',
      dtype: 'q4',
      progress_callback: (p) => self.postMessage({ type: 'progress', ...p }),
    });
    self.postMessage({ type: 'loaded' });
    return;
  }

  if (type === 'translate') {
    const result = await translator(text, {
      src_lang: sourceLang,
      tgt_lang: targetLang,
    });
    self.postMessage({ type: 'result', translation: result[0].translation_text });
  }
};
```

---

## 4. Data Flow: Real-Time Translation

```
Timeline (milliseconds):
─────────────────────────

0ms      User types "k"
10ms     User types "a"
20ms     User types "l"
...
270ms    User types "g" (finishing "kal meeting")
280ms    Debounce starts (250ms countdown from last keystroke)
...
530ms    ⏰ Debounce fires! (user paused for 250ms)

CLIENT-SIDE PATH (Tier 1+2):
531ms    Check IndexedDB cache → MISS
532ms    Check if NLLB-200 is loaded → YES
533ms    Post message to Web Worker: translate("kal meeting", "hin_en", "en")
534ms    Web Worker starts NLLB-200 inference (WebGPU)
634ms    Translation complete: "Tomorrow's meeting"
635ms    Output panel renders: "Tomorrow's meeting"
636ms    Cache result in IndexedDB

Total perceived latency: ~105ms (from debounce fire to visible output)
Zero network requests. Zero cost. Works offline.

EDGE FALLBACK PATH (Tier 3):
531ms    Check IndexedDB cache → MISS
532ms    Check if NLLB-200 is loaded → NO (still downloading)
533ms    POST /api/translate { text: "kal meeting", source: "hinglish", target: "en" }
550ms    Cloudflare Worker validates + rate checks
560ms    Routes to Supabase Edge Function
600ms    IndicTrans3 processes translation
700ms    Response arrives: "Tomorrow's meeting"
701ms    Output panel renders
702ms    Cache result in IndexedDB

Total perceived latency: ~170ms (network needed)
```

---

## 5. Caching Strategy

### 5.1 Multi-Layer Cache

```
Layer 1: IndexedDB (Browser — Persistent)
├── All translation results cached locally
├── Key: hash(source + target + normalized_text)
├── Instant lookup (< 5ms)
├── Survives page reload and browser restart
├── TTL: 30 days
└── Max entries: 500 (LRU eviction)

Layer 2: NLLB-200 Model Cache (IndexedDB)
├── ~150MB model weights stored persistently
├── Downloaded once, cached forever
├── Only re-downloaded on model version update
└── Checked on app load → skip download if present

Layer 3: Edge Cache (Supabase/Cloudflare)
├── Server-side cache for Tier 3 responses
├── Shared across all users
├── TTL: 24 hours
└── Only relevant for edge fallback path
```

### 5.2 Cache Key Normalization

Before hashing, input text is normalized:
1. Convert to lowercase
2. Collapse multiple spaces
3. Remove trailing punctuation
4. Trim whitespace

This ensures "Kal Meeting" and "kal meeting" hit the same cache entry.

---

## 6. Prompt Engineering Architecture

System prompts are still critical for Tier 3 (IndicTrans3 / Gemma 3) and are stored in `lib/prompts.js`. The prompt library from v1.0 remains fully applicable — see [03-ai-ml-models.md](file:///d:/Learning-Tutorials/Apni%20Bhasha/docs/03-ai-ml-models.md) for the complete prompt set.

For Tier 2 (NLLB-200), no prompts are needed — the model uses language codes directly:

```javascript
// NLLB-200 uses ISO language codes, not prompts
const result = await translator(inputText, {
  src_lang: 'hin_Latn',   // Hindi in Latin script
  tgt_lang: 'eng_Latn',   // English
});
```

---

## 7. Security Architecture

### 7.1 Revised Threat Model

The client-side-first approach **eliminates** several threats from v1.0:

| Threat | v1.0 (Cloud API) | v2.0 (Client-Side First) |
|--------|------------------|--------------------------|
| **Denial of Wallet** | HIGH — API costs scale with attacks | **LOW** — 80%+ of requests are free (in-browser) |
| **Prompt Injection** | HIGH — User input sent to LLM | **LOW** — NLLB-200 uses language codes, not prompts. Only Tier 3 uses prompts. |
| **API Key Exposure** | MEDIUM — Keys on server | **LOW** — Fewer API keys needed; most inference is client-side |
| **Data Privacy** | MEDIUM — Data sent to Google/OpenAI | **NONE** — Data stays on device for Tier 1+2 |
| **Bot Scraping** | MEDIUM | **LOW** — Nothing to scrape; model runs locally |
| **XSS / Injection** | Same | Same — still sanitize all input/output |

### 7.2 Remaining Protections (Tier 3 only)

```
Cloudflare Worker:
├── Rate limiting: 100K requests/day (free tier)
├── IP-based throttling: 60 req/min per IP
├── Bot score filtering
└── DDoS protection (automatic)

Supabase Edge Function:
├── Input sanitization
├── Output length validation
├── Request authentication (optional, for logged-in users)
└── Abuse logging
```

---

## 8. Technology Stack Summary

| Layer | Technology | Cost |
|-------|-----------|------|
| **Framework** | Next.js 16 (App Router, PPR) | Free |
| **Styling** | Tailwind CSS + Shadcn UI | Free |
| **Tier 1: Transliteration** | Aksharamukha.js (< 1MB, browser) | Free |
| **Tier 1: Language Detection** | fastText LID (~1MB, browser) | Free |
| **Tier 2: Translation** | Transformers.js v4 + NLLB-200 (browser, WebGPU) | Free |
| **Tier 3: Translation** | IndicTrans3 + Gemma 3 4B (edge/server) | Free tier |
| **Tier 3: Transliteration** | Indic-Xlit (edge/server) | Free |
| **Database** | Supabase (PostgreSQL) | Free tier |
| **Edge Compute** | Cloudflare Workers (rate limiting) | Free (100K/day) |
| **Hosting** | Vercel | Free tier |
| **CDN / WAF** | Cloudflare | Free |
| **TTS** | Web Speech API | Free (browser built-in) |
| **Analytics** | PostHog | Free (1M events/month) |
| **Total Monthly Cost** | | **$0 — $5** for 10K MAU |

---

## 9. Scalability Path

```
Phase 1 (MVP): 0 — 10K MAU
├── Client-side NLLB-200 handles 80%+ of requests
├── Supabase free tier for Tier 3 fallback
├── Cloudflare free tier for rate limiting
├── Cost: $0 — $5/month
│
Phase 2 (Growth): 10K — 100K MAU
├── Add user accounts via Supabase Auth
├── Crowdsource translation corrections
├── Upgrade Supabase to Pro ($25/month)
├── Add IndicTrans3 on Modal for best Indic accuracy
├── Cost: $30-80/month
│
Phase 3 (Scale): 100K+ MAU
├── Fine-tune Gemma 3 4B with LoRA on proprietary dataset
├── Self-host on Modal / RunPod
├── Custom ONNX export for client-side fine-tuned model
├── Replace NLLB-200 with domain-specific model
├── Cost: $100-300/month (offset by revenue)
```

---

## 10. Error Handling Strategy

| Scenario | Behavior |
|----------|----------|
| WebGPU not supported | Fall back to WASM for Tier 2; if too slow, route to Tier 3 |
| NLLB-200 model download fails | Continue using Tier 3 (edge); retry download on next visit |
| NLLB-200 inference crashes (GPU OOM) | Catch error, route to Tier 3, flag device as low-capability |
| Tier 3 edge function timeout | Retry once, then show "Translation unavailable" |
| Network offline + no model loaded | Show "Download the AI model for offline translation" prompt |
| Network offline + model loaded | Translate fully offline via Tier 2 — show "Offline" badge |
| Invalid language pair | Disable swap button, show helpful error |
| Empty input | No translation call, clear output panel |
| Input too long (> 500 chars) | Truncate with warning, translate first 500 chars |
