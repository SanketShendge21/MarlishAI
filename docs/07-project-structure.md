# Marlish.AI — Project Directory Structure

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Current

---

```
MarlishAI/
│
├── app/                              # Next.js 16 frontend (App Router)
│   ├── page.js                       # Main translator page
│   ├── layout.js                     # Root layout (fonts, metadata, PostHog)
│   ├── globals.css                   # Global styles
│   ├── not-found.js                  # 404 page
│   ├── favicon.ico
│   └── components/
│       ├── translator/
│       │   ├── TranslatorPanel.jsx   # Main translator container
│       │   ├── InputArea.jsx         # Text input with char counter
│       │   ├── OutputArea.jsx        # Translation output display
│       │   ├── LanguageSelector.jsx  # Language dropdowns
│       │   └── SwapButton.jsx        # Swap source ↔ target
│       ├── actions/
│       │   └── ActionBar.jsx         # Copy, share, history
│       └── ui/
│           ├── Header.jsx            # App header/logo
│           ├── Footer.jsx            # App footer
│           └── OfflineIndicator.jsx  # Offline status banner
│
├── api/
│   └── app.py                        # FastAPI translation API (v2.0)
│                                     #   POST /translate, GET /health
│                                     #   NLLB-200-1.3B + transliteration
│                                     #   Gemini GEC post-processing
│
├── scripts/
│   ├── transliterator/               # Custom transliteration pipeline
│   │   ├── __init__.py
│   │   ├── pipeline.py               # 3-tier orchestrator
│   │   ├── fallback_map.py           # 400+ word seed map (Tier 2)
│   │   ├── phoneme_rules.py          # Character-level rules (Tier 3)
│   │   ├── reverse_transliterate.py  # Devanagari → romanized
│   │   └── token_classifier.py       # English vs Marlish detection
│   ├── test_carnival_tours.py        # 104-segment quality test (all 8 dirs)
│   └── test_translation_quality.py   # 23-sentence quality test
│
├── hooks/
│   ├── useTranslation.js             # React hook → API calls
│   └── useDebounce.js                # Adaptive debounce (300-800ms)
│
├── lib/
│   └── local-cache.js                # localStorage history manager
│
├── docs/
│   ├── 01-requirements.md            # Functional/non-functional specs
│   ├── 02-architecture.md            # System architecture
│   ├── 03-ai-ml-models.md            # Model selection & strategy
│   ├── 04-use-cases.md               # Use cases & examples
│   ├── 05-deployment.md              # Deployment guide
│   ├── 06-research-prompts.md        # Research reference (archive)
│   ├── 07-project-structure.md       # This file
│   ├── 08-tech-stack.md              # Technology stack
│   ├── 09-app-vision-and-goals.md    # Vision & roadmap
│   ├── 10-ml-model-roadmap.md        # ML model evolution
│   ├── 11-enterprise-architecture.md # Enterprise considerations
│   ├── progress_tracker.md           # Development roadmap & state
│   ├── carnival_tours_original.txt   # Test data (Marathi)
│   └── test-results/                 # Test output files
│       ├── CARNIVAL_TEST_RESULTS.md
│       └── TRANSLATION_TEST_RESULTS.md
│
├── Dockerfile                        # HF Spaces Docker build
├── .dockerignore                     # Docker build exclusions
├── requirements-api.txt              # Python API deps (production)
├── requirements.txt                  # Python dev/research deps
├── README.md                         # Main project README
├── README_HF.md                      # HF Spaces README
├── SETUP_ML.md                       # ML environment setup guide
├── vercel.json                       # Vercel deployment config
├── package.json                      # Node.js deps
├── next.config.mjs                   # Next.js config
├── postcss.config.mjs                # PostCSS (Tailwind)
├── .gitignore                        # Git exclusions
└── .local.env                        # API keys (not committed)
```

## Key Directories

| Directory | Purpose | Deployed To |
|-----------|---------|-------------|
| `app/` | Next.js frontend | Vercel |
| `api/` | FastAPI backend | HF Spaces |
| `scripts/transliterator/` | Transliteration pipeline | HF Spaces (with API) |
| `hooks/` | React hooks | Vercel (with frontend) |
| `docs/` | Documentation | Not deployed |
| `scripts/test_*.py` | Test scripts | Not deployed |
