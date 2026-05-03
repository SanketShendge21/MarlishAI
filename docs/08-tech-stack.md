# Marlish.AI — Technology Stack (Open-Source First)

> **Version:** 2.0 | **Date:** 2026-04-19 | **Status:** Updated
>
> This document supersedes the tech stack sections in earlier documents.
> The architecture has been revised to prioritize **free, open-source, and
> client-side-first** technologies wherever possible.

---

## 1. Stack Philosophy

The revised stack follows three principles:

1. **Zero API Cost** — Translation runs in-browser via WebGPU wherever possible
2. **No Vendor Lock-In** — Every component is open-source or has a free-tier alternative
3. **Progressive Enhancement** — Client-side models handle fast tasks; edge fallback handles complex ones

---

## 2. Complete Technology Stack

### 2.1 Frontend & UI Framework

| Technology | Role | Why Chosen |
|-----------|------|-----------|
| **Next.js 16** | App framework | Partial Prerendering (PPR) delivers a static HTML shell instantly while streaming dynamic content. Best-in-class edge function support. |
| **Tailwind CSS** | Styling | Utility-first, purges unused CSS for minimal payload. Essential for rapid mobile-first development. |
| **Shadcn UI** | UI Components | Accessible, unstyled components (dropdowns, inputs, dialogs) copied directly into the project. Zero runtime dependency — complete design control. |

### 2.2 In-Browser AI Engine

| Technology | Role | Why Chosen |
|-----------|------|-----------|
| **Transformers.js v4** | Client-side ML runtime | Runs ONNX models 100% locally in the browser. v4 uses WebGPU backend for hardware-accelerated inference — up to 64x faster than WASM. Eliminates backend API costs entirely. |
| **WebGPU API** | Hardware acceleration | Direct GPU access in the browser. Supported in Chrome 113+, Edge 113+, Firefox (behind flag). Falls back to WASM on unsupported devices. |
| **ONNX Runtime Web** | Model execution | Underlying runtime that Transformers.js v4 leverages. Optimized for quantized model inference on web. |

### 2.3 Translation Models (Free & Open-Source)

| Model | Parameters | Size (Quantized) | Use Case | Source |
|-------|-----------|-------------------|----------|--------|
| **NLLB-200 (Distilled 600M)** | 600M | ~242MB (q4: ~150MB) | Primary in-browser translation across 200 languages. Quantized ONNX weights packaged for Transformers.js. Cached in IndexedDB after first load. | Meta AI |
| **IndicTrans3** | Varies | Server-side | High-accuracy Indic translation (15 languages). Built on Gemma-3 architecture. Exceptional for document-level and sentence-level Hindi/Marathi/English. Best cultural accuracy. | AI4Bharat |
| **Gemma 3 (4B)** | 4B | ~2.5GB (q4) | Complex Romanized Hinglish/Marlish parsing. 140+ language support. Use as edge fallback for code-mixed sentences that NLLB-200 cannot handle. | Google (open-weight) |

### 2.4 Transliteration Libraries

| Library | Type | Size | Use Case |
|---------|------|------|----------|
| **Aksharamukha.js** | Rule-based, browser-compatible | < 1MB | Instantaneous Roman ↔ Devanagari script conversion across 100+ Indic scripts. 100% offline, zero latency. Perfect for real-time phonetic typing previews. |
| **Indic-Xlit** (AI4Bharat) | ML-based, Python/API | ~50MB | Optimized for colloquially-typed Roman text → native Indic scripts. Handles ad-hoc spelling variations and vowel-dropped input. Runs on edge/server. |

### 2.5 Language Identification

| Model | Size | Use Case |
|-------|------|----------|
| **fastText LID (lid.176.ftz)** | ~1MB | Quick sentence-level language detection (176 languages). Runs client-side. |
| **L3Cube-MeLID** | ~10MB | Token-level Marathi-English code-mix identification. |

### 2.6 Backend & Database

| Technology | Role | Free Tier | Why Chosen |
|-----------|------|-----------|-----------|
| **Supabase** | Database + Auth + Edge Functions | PostgreSQL, 500MB storage, 50K MAU auth, 500K edge invocations/month | Best backend for solo developers. Stores user preferences, translation history, and crowdsourced corrections. Real-time subscriptions built-in. |
| **Cloudflare Workers** | Edge compute + Rate limiting | 100,000 requests/day free | Essential for cost-aware rate limiting, bot protection, and routing complex translation requests to server-side models when client-side inference isn't sufficient. |

### 2.7 Hosting & CDN

| Technology | Role | Free Tier | Why Chosen |
|-----------|------|-----------|-----------|
| **Vercel** | Frontend hosting | 100GB bandwidth, serverless functions, edge network | Native Next.js 16 optimization. Seamless GitHub CI/CD. Mumbai edge PoP for Indian users. |
| **Cloudflare** | CDN + WAF + DDoS | Unlimited bandwidth, DNS, SSL, page rules | Global CDN for static assets. Advanced rate limiting. Bot management. |

### 2.8 Supporting Tools

| Technology | Role | Cost |
|-----------|------|------|
| **Web Speech API** | Text-to-Speech | Free (browser built-in) |
| **PostHog** | Analytics | Free (1M events/month) |
| **Sentry** | Error tracking | Free (5K errors/month) |
| **next-pwa** | PWA support | Free (open-source) |

---

## 3. Architecture Tiers

The revised architecture has **three inference tiers**:

```
┌──────────────────────────────────────────────────────────────────┐
│                    TIER 1: CLIENT-SIDE (Instant)                  │
│                                                                  │
│  Aksharamukha.js          → Transliteration (Roman ↔ Devanagari) │
│  fastText LID             → Language detection                   │
│  Local cache (IndexedDB)  → Previously seen translations         │
│                                                                  │
│  Latency: < 10ms | Cost: $0 | Works offline                     │
└──────────────────────────┬───────────────────────────────────────┘
                           │ (if transliteration not sufficient)
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    TIER 2: IN-BROWSER ML (Fast)                   │
│                                                                  │
│  Transformers.js v4 + WebGPU                                     │
│  NLLB-200 (Distilled 600M, quantized)                            │
│  Cached in IndexedDB after first download (~150MB q4)            │
│                                                                  │
│  Latency: 100-500ms | Cost: $0 | Needs WebGPU-capable device    │
└──────────────────────────┬───────────────────────────────────────┘
                           │ (if device can't run model OR
                           │  complex code-mixed input detected)
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    TIER 3: EDGE/SERVER (Accurate)                 │
│                                                                  │
│  Cloudflare Worker → Supabase Edge Function                      │
│  IndicTrans3 (AI4Bharat) for high-accuracy Indic translation     │
│  Gemma 3 4B for complex Romanized code-mixed parsing             │
│  Indic-Xlit for colloquial transliteration                       │
│                                                                  │
│  Latency: 200-800ms | Cost: Compute only | Always available      │
└──────────────────────────────────────────────────────────────────┘
```

### Tier Selection Logic

```javascript
function selectTier(input, sourceLang, targetLang, deviceCapabilities) {
  // TIER 1: Pure transliteration (Roman ↔ Script conversion)
  if (isTransliterationOnly(sourceLang, targetLang)) {
    return 'aksharamukha';  // < 10ms, offline
  }

  // TIER 1: Check local cache
  const cached = await localCache.get(input, sourceLang, targetLang);
  if (cached) return cached;  // < 5ms, offline

  // TIER 2: In-browser NLLB-200 (if device supports WebGPU)
  if (deviceCapabilities.webgpu && isModelLoaded('nllb-200')) {
    return await runNLLB200(input, sourceLang, targetLang);  // 100-500ms
  }

  // TIER 3: Edge fallback (complex code-mixed or low-end device)
  return await callEdgeTranslation(input, sourceLang, targetLang);  // 200-800ms
}
```

---

## 4. Model Loading Strategy

### 4.1 First Visit (Cold Start)

```
Page loads (< 1.2s FCP via Next.js PPR)
  │
  ├── Aksharamukha.js loads instantly (< 1MB) → Transliteration ready
  │
  ├── Background: Start downloading NLLB-200 ONNX model (~150MB q4)
  │   ├── Show progress bar: "Loading AI model for offline translation..."
  │   ├── Store in IndexedDB (persistent cache)
  │   └── While downloading → use TIER 3 (edge) for translations
  │
  └── User can start translating immediately (via edge fallback)
```

### 4.2 Return Visit (Warm Start)

```
Page loads (< 1.2s FCP)
  │
  ├── Aksharamukha.js loads instantly
  │
  ├── NLLB-200 loaded from IndexedDB cache (< 2s)
  │   └── No network download needed
  │
  └── Full offline translation ready in < 3 seconds
```

### 4.3 Model Caching with IndexedDB

```javascript
// Check if model is already cached
const modelCached = await caches.has('nllb-200-distilled-600m-q4');

if (modelCached) {
  // Load from IndexedDB — no network needed
  const pipeline = await pipeline('translation', 'Xenova/nllb-200-distilled-600M', {
    device: 'webgpu',          // Use GPU acceleration
    dtype: 'q4',               // 4-bit quantized
    cache_dir: 'indexeddb',    // Persistent browser cache
  });
} else {
  // First-time download with progress callback
  const pipeline = await pipeline('translation', 'Xenova/nllb-200-distilled-600M', {
    device: 'webgpu',
    dtype: 'q4',
    progress_callback: (progress) => {
      updateProgressBar(progress.progress);  // Show download %
    },
  });
}
```

---

## 5. Open-Source Model Hosting (Tier 3)

For the server-side fallback models (IndicTrans3, Gemma 3 4B), several free/cheap options exist:

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Hugging Face Inference Endpoints** | Free (rate-limited) | Testing IndicTrans3 |
| **Google Colab / Kaggle** | Free GPU (limited hours) | Prototyping with Gemma 3 |
| **Supabase Edge Functions** | 500K invocations/month | Lightweight routing logic |
| **Cloudflare Workers AI** | 10K neurons/day free | Running small models at edge |
| **Modal** | $30 free credits | Serverless GPU for IndicTrans3 |
| **Replicate** | Free tier available | API-style model serving |

### Recommended Tier 3 Setup (MVP)

```
Option A (Simplest): 
  Supabase Edge Function → calls Hugging Face Inference API (IndicTrans3)
  Cost: $0 (within free tiers)

Option B (Best quality):
  Cloudflare Worker → routes to Modal (IndicTrans3 on GPU)
  Cost: ~$5-10/month at 10K DAU

Option C (Best latency):
  Cloudflare Workers AI → runs small quantized model directly
  Cost: $0 (within 10K neurons/day)
```

---

## 6. Cost Comparison: Old vs New Stack

| | Old Stack (Cloud API) | New Stack (Open-Source) |
|--|----------------------|----------------------|
| **Translation Engine** | Gemini Flash-Lite / GPT-4o-mini | Transformers.js + NLLB-200 (client-side) |
| **Cost per 1K translations** | $0.03 — $0.07 | **$0.00** (client-side) |
| **Monthly cost @ 1K DAU** | ~$18/month | **~$1/month** (domain only) |
| **Monthly cost @ 10K DAU** | ~$108/month | **~$5-10/month** (Tier 3 fallback only) |
| **Monthly cost @ 100K DAU** | ~$1,080/month | **~$30-50/month** |
| **Offline support** | None | Full (after model download) |
| **Privacy** | Data sent to Google/OpenAI | Data stays on device |
| **Vendor lock-in** | High (API dependency) | None |

---

## 7. Dependency List

### Production Dependencies

```json
{
  "dependencies": {
    "next": "^16.0.0",
    "@xenova/transformers": "^4.0.0",
    "aksharamukha": "latest",
    "@supabase/supabase-js": "^2.0.0",
    "posthog-js": "^1.0.0"
  },
  "devDependencies": {
    "tailwindcss": "^4.0.0",
    "@tailwindcss/postcss": "latest",
    "autoprefixer": "latest",
    "vitest": "latest"
  }
}
```

### CDN / External Resources

```
Google Fonts: Inter (UI), Noto Sans Devanagari (Indic output)
Hugging Face Hub: NLLB-200 ONNX weights (cached in IndexedDB)
```

---

## 8. Browser Compatibility Matrix

| Feature | Chrome 113+ | Edge 113+ | Firefox 120+ | Safari 18+ | Mobile Chrome |
|---------|:-----------:|:---------:|:------------:|:----------:|:------------:|
| **WebGPU** | ✅ | ✅ | ⚠️ Flag | ✅ | ⚠️ Limited |
| **WASM Fallback** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **IndexedDB** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Web Speech API** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Service Worker** | ✅ | ✅ | ✅ | ✅ | ✅ |

**Strategy:** Use WebGPU where available for fastest inference. Fall back to WASM on unsupported devices (still client-side, just slower). If device is too constrained (< 2GB RAM), route to Tier 3 edge.

---

## 9. Key Trade-Offs

| Decision | Pro | Con | Mitigation |
|----------|-----|-----|-----------|
| NLLB-200 in browser | $0 cost, offline, private | ~150MB initial download | Progressive loading with edge fallback during download |
| Aksharamukha over IndicXlit client-side | < 1MB, instant, offline | Rule-based (less flexible for ad-hoc spelling) | Use IndicXlit on server (Tier 3) for hard cases |
| IndicTrans3 on server only | Best Indic accuracy | Requires server compute | Only used for Tier 3 fallback; most requests handled client-side |
| WebGPU requirement for Tier 2 | 64x faster than WASM | Not universal yet | WASM fallback + Tier 3 edge as safety net |
| Supabase over custom backend | Free, managed, real-time | Less control | Edge functions for custom logic |
