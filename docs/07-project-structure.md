# Marlish.AI — Project Directory Structure

> **Version:** 2.0 | **Date:** 2026-04-19 (Updated: Open-Source First)

---

## Complete Project Tree

```
marlish-ai/
│
├── 📄 README.md                          # Project overview + quickstart
├── 📄 .gitignore                         # Git ignore rules
├── 📄 .env.example                       # Template for environment variables
├── 📄 package.json                       # Dependencies + scripts
├── 📄 pnpm-lock.yaml                    # Lock file (pnpm)
├── 📄 next.config.js                    # Next.js configuration
├── 📄 vercel.json                       # Vercel deployment config (regions, headers)
├── 📄 tailwind.config.js               # Tailwind CSS configuration
├── 📄 postcss.config.js                # PostCSS config for Tailwind
├── 📄 jsconfig.json                    # Path aliases (@/components, etc.)
│
├── 📁 docs/                             # Project documentation
│   ├── 📄 01-requirements.md            # Functional + non-functional requirements
│   ├── 📄 02-architecture.md            # System architecture + data flow
│   ├── 📄 03-ai-ml-models.md           # AI/ML model strategy + prompts
│   ├── 📄 04-use-cases.md              # Use cases + user personas
│   ├── 📄 05-deployment.md             # Deployment guide + infrastructure
│   ├── 📄 06-research-prompts.md       # Prompts for language research
│   ├── 📄 07-project-structure.md      # This file
│   ├── 📄 08-tech-stack.md             # Technology stack (open-source first)
│   │
│   ├── 📁 prompts/                      # Step-by-step implementation prompts
│   │   ├── 📄 README.md                # Build order index + time estimates
│   │   ├── 📄 01-project-setup.md      # Next.js scaffold, Tailwind, structure
│   │   ├── 📄 02-ui-layout.md          # Complete translator UI + design system
│   │   ├── 📄 03-tier1-transliteration.md  # Aksharamukha, IndexedDB, LID
│   │   ├── 📄 04-tier2-nllb-browser.md # NLLB-200 in browser, Web Worker
│   │   ├── 📄 05-tier-router.md        # Three-tier router, debounce, hooks
│   │   ├── 📄 06-tier3-edge-fallback.md # HuggingFace API, edge route
│   │   ├── 📄 07-actions-features.md   # Copy, TTS, Share, History
│   │   ├── 📄 08-pwa-offline.md        # Service worker, offline, install
│   │   └── 📄 09-polish-deploy.md      # Animations, SEO, Vercel deploy
│   │
│   └── 📁 research/                     # Research outputs (from prompt responses)
│       ├── 📄 hinglish-analysis.md
│       ├── 📄 marlish-analysis.md
│       └── 📄 test-cases.md
│
├── 📁 public/                           # Static assets (served at root)
│   ├── 📄 favicon.ico                  # Browser tab icon
│   ├── 📄 icon-192.png                 # PWA icon (192x192)
│   ├── 📄 icon-512.png                 # PWA icon (512x512)
│   ├── 📄 apple-touch-icon.png        # iOS home screen icon
│   ├── 📄 manifest.json               # PWA manifest
│   ├── 📄 robots.txt                   # Search engine directives
│   └── 📄 og-image.png                # Open Graph image for social sharing
│
├── 📁 app/                              # Next.js App Router (main application)
│   ├── 📄 layout.js                    # Root layout: HTML, fonts, theme, metadata
│   ├── 📄 page.js                      # Home page: main translator UI
│   ├── 📄 globals.css                  # Global styles + Tailwind directives
│   ├── 📄 not-found.js                # Custom 404 page
│   │
│   ├── 📁 api/                          # API routes (Edge Functions)
│   │   └── 📁 translate/
│   │       └── 📄 route.js             # POST /api/translate — TIER 3 FALLBACK ONLY
│   │                                    #   - Only called when client-side fails
│   │                                    #   - Routes to IndicTrans3 / Gemma 3
│   │                                    #   - Rate limited via Cloudflare
│   │
│   └── 📁 components/                   # React components
│       ├── 📁 translator/               # Core translator components
│       │   ├── 📄 TranslatorPanel.jsx  # Main container: input + output panels
│       │   ├── 📄 InputArea.jsx        # Textarea with auto-focus + clear button
│       │   ├── 📄 OutputArea.jsx       # Streaming output display + loading state
│       │   ├── 📄 LanguageSelector.jsx # Dropdown for source/target language
│       │   └── 📄 SwapButton.jsx       # Animated language swap toggle
│       │
│       ├── 📁 actions/                  # Action/utility components
│       │   ├── 📄 ActionBar.jsx        # Bottom bar: Copy, TTS, Share, History
│       │   ├── 📄 CopyButton.jsx       # Copy to clipboard with checkmark anim
│       │   ├── 📄 TTSButton.jsx        # Text-to-Speech trigger
│       │   ├── 📄 ShareButton.jsx      # WhatsApp share deep link
│       │   └── 📄 HistoryDrawer.jsx    # Slide-up drawer for recent translations
│       │
│       ├── 📁 ai/                       # AI-related UI components
│       │   ├── 📄 ModelLoader.jsx      # NLLB-200 download progress bar
│       │   └── 📄 TierIndicator.jsx    # Shows active tier (Local/Edge)
│       │
│       └── 📁 ui/                       # Generic UI primitives
│           ├── 📄 ThemeToggle.jsx      # Dark/Light mode switch
│           ├── 📄 Header.jsx           # App header: logo + theme toggle
│           ├── 📄 Footer.jsx           # Minimal footer: privacy + credits
│           ├── 📄 LoadingSkeleton.jsx  # Shimmer/pulse loading animation
│           └── 📄 Toast.jsx            # Toast notification component
│
├── 📁 hooks/                            # Custom React hooks
│   ├── 📄 useTranslation.js           # Core hook: tier routing + debounce + abort
│   │                                    #   - Routes to Tier 1/2/3 based on context
│   │                                    #   - Manages translation lifecycle
│   │                                    #   - Error state management
│   ├── 📄 useModelLoader.js           # NLLB-200 loading + progress + IndexedDB cache
│   ├── 📄 useTransliterate.js         # Aksharamukha.js wrapper for Tier 1
│   ├── 📄 useDebounce.js              # Generic debounce hook (configurable ms)
│   ├── 📄 useTheme.js                 # System theme detection + toggle + persist
│   ├── 📄 useClipboard.js             # Clipboard API wrapper with feedback
│   └── 📄 useTTS.js                   # Web Speech API wrapper
│
├── 📁 lib/                              # Shared utilities + configuration
│   ├── 📄 tier-router.js              # Decides Tier 1/2/3 based on input + device
│   │                                    #   - Checks capabilities (WebGPU, model loaded)
│   │                                    #   - Routes to appropriate inference path
│   ├── 📄 aksharamukha.js             # Aksharamukha.js transliteration wrapper
│   │                                    #   - Roman ↔ Devanagari (100+ scripts)
│   │                                    #   - 100% offline, < 1MB
│   ├── 📄 nllb-pipeline.js            # Transformers.js NLLB-200 pipeline setup
│   │                                    #   - WebGPU/WASM device selection
│   │                                    #   - 4-bit quantized model loading
│   ├── 📄 language-detect.js          # fastText LID integration (~1MB)
│   ├── 📄 prompts.js                   # System prompts for Tier 3 (5 language pairs)
│   │                                    #   - Only used for edge/server fallback
│   ├── 📄 languages.js                 # Language definitions + valid pair mappings
│   │                                    #   - { code, label, script, nllbCode }
│   │                                    #   - Valid pairs matrix
│   ├── 📄 constants.js                 # App-wide constants
│   │                                    #   - DEBOUNCE_MS = 250
│   │                                    #   - MAX_INPUT_LENGTH = 500
│   │                                    #   - NLLB_MODEL_ID
│   ├── 📄 local-cache.js              # IndexedDB cache for translations
│   │                                    #   - get/set with LRU eviction
│   │                                    #   - 500 entries, 30-day TTL
│   ├── 📄 sanitize.js                 # Input sanitization utilities
│   │                                    #   - stripHTML(), truncate(), escape()
│   └── 📄 analytics.js                # PostHog event tracking wrapper
│
├── 📁 workers/                          # Web Workers (off-main-thread)
│   └── 📄 nllb-worker.js              # NLLB-200 inference in Web Worker
│                                        #   - Keeps UI thread responsive
│                                        #   - Loads model, runs translation
│                                        #   - Communicates via postMessage
│
├── 📁 tests/                            # Test suites
│   ├── 📄 translation.test.js         # Translation accuracy tests
│   │                                    #   - Test cases for all 5 language pairs
│   │                                    #   - Edge cases: ambiguity, slang, vowel drop
│   ├── 📄 debounce.test.js            # Debounce + AbortController behavior tests
│   ├── 📄 rate-limiter.test.js        # Rate limiting logic tests
│   ├── 📄 sanitize.test.js            # Input sanitization tests
│   ├── 📄 cache.test.js               # Cache key generation + normalization tests
│   └── 📁 fixtures/                    # Test data
│       ├── 📄 hinglish-en.json        # Hinglish → English test pairs
│       ├── 📄 hinglish-mr.json        # Hinglish → Marathi test pairs
│       ├── 📄 en-mr.json              # English → Marathi test pairs
│       ├── 📄 marlish-en.json         # Marlish → English test pairs
│       └── 📄 marlish-hi.json         # Marlish → Hindi test pairs
│
└── 📁 scripts/                          # Utility scripts
    ├── 📄 seed-cache.js               # Pre-warm cache with top 1000 phrases
    ├── 📄 test-prompts.js             # Test all prompts against LLM APIs
    └── 📄 benchmark.js                # Measure translation latency + accuracy
```

---

## Key Design Principles

### 1. Flat Component Hierarchy
Components are organized by domain (`translator/`, `actions/`, `ui/`) rather than atomic design (atoms/molecules/organisms). This is more intuitive for a single-purpose app.

### 2. Hooks as Business Logic Layer
All stateful business logic lives in `hooks/`. Components are purely presentational. This enables easy testing and refactoring.

### 3. `lib/` as the Intelligence Layer
The `lib/` directory contains the three-tier routing logic, model wrappers (Aksharamukha, NLLB-200), and caching. The `tier-router.js` is the brain that decides where each translation request goes.

### 4. Web Worker for Heavy Inference
NLLB-200 runs in a Web Worker (`workers/nllb-worker.js`) to keep the UI thread completely responsive during translation. This is critical for the "as-you-type" experience.

### 5. Single API Endpoint (Tier 3 Only)
The API route `POST /api/translate` is only called as a fallback. Most requests never leave the browser.

---

## Tech Stack Quick Reference

| Category | Choice | File(s) |
|----------|--------|---------|
| Framework | Next.js 16 (App Router) | `next.config.js`, `app/` |
| Styling | Tailwind CSS + Shadcn UI | `tailwind.config.js`, `globals.css` |
| Tier 1: Transliteration | Aksharamukha.js (browser, < 1MB) | `lib/aksharamukha.js` |
| Tier 1: Language Detection | fastText LID (browser, ~1MB) | `lib/language-detect.js` |
| Tier 2: Translation | Transformers.js v4 + NLLB-200 (WebGPU) | `lib/nllb-pipeline.js`, `workers/nllb-worker.js` |
| Tier 3: Translation | IndicTrans3 / Gemma 3 (edge) | `app/api/translate/route.js` |
| Tier 3: Transliteration | Indic-Xlit (edge) | `app/api/translate/route.js` |
| Tier Routing | Custom three-tier router | `lib/tier-router.js` |
| Local Cache | IndexedDB (browser) | `lib/local-cache.js` |
| Database | Supabase (PostgreSQL) | via `@supabase/supabase-js` |
| Hosting | Vercel | `vercel.json` |
| CDN/WAF | Cloudflare | External config |
| Analytics | PostHog | `lib/analytics.js` |
