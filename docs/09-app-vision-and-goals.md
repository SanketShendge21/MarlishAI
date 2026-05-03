# Marlish.AI — Vision, Goals & Architecture

> **Version:** 6.0 | **Date:** 2026-05-03 | **Status:** Production-Ready (Offline 7-Layer NLP Dictionary)

---

## 1. What Is Marlish.AI?

**Marlish.AI** is a real-time, offline-first translation web app for conversational Indian languages. It translates the way Indians actually text — in Hinglish (Hindi + English), Marlish (Marathi + English), and other mixed-code variants — using curated JSON dictionaries powered by a custom **7-layer NLP translation engine**.

### Supported Language Pairs

| Source | Target | Type | Route |
|--------|--------|------|-------|
| Hinglish | English | Direct | `hinglish_phrases` + `hinglish_words` |
| English | Hinglish | Direct (Reverse) | `english_to_hinglish_*` |
| Marlish | English | Direct | `marlish_phrases` + `marlish_words` |
| English | Marlish | Direct (Reverse) | `english_to_marlish_*` |
| Hinglish | Marlish | **Pivot** | Hinglish → English → Marlish |
| Marlish | Hinglish | **Pivot** | Marlish → English → Hinglish |
| Marathi | English | Direct | Treated as Marlish lookup |
| Hindi | English | Direct | Treated as Hinglish lookup |
| English | Marathi | Direct | Routed to English → Marlish |
| English | Hindi | Direct | Routed to English → Hinglish |

**Swap button** works for ALL pairs — swaps languages and moves translation to input.

---

## 2. Why JSON Over CSV?

We migrated from a 10MB CSV to an optimized JSON dictionary built from three source datasets:

| Dataset | Content | Entries |
|---------|---------|---------|
| `hinglish_marlish_10000_dataset.json` (v1) | Individual words | 5,000 Hinglish + 5,000 Marlish |
| `hinglish_marlish_v2_25000_dataset.json` (v2) | Full phrases | 12,500 Hinglish + 12,500 Marlish |
| `hinglish_marlish_v3_production_100k.json` (v3) | Full phrases | 50,000 Hinglish + 50,000 Marlish (reserve) |

**Production file:** `public/dictionary.json` (~1.2MB) — combines v1 words + v2 phrases + reverse maps.

| Metric | Old CSV | New JSON |
|--------|---------|----------|
| File size | 10MB | **1.2MB** |
| Unique entries | 5 | **35,051+** |
| Parse library needed | PapaParse | **Native JSON.parse** |
| Load time | ~200ms | **~50ms** |

---

## 3. The 7-Layer NLP Translation Engine

To overcome the robotic "word-for-word" translations of simple dictionaries, we built a highly advanced, stateless 7-layer rule engine (`lib/dictionary-engine.js`).

### Layer 1: Normalization (Typo Handling)
Cleans up casual chat abbreviations before translation:
- `"kr"` → `"kar"`, `"rha"` → `"raha"`

### Layer 2: Intent & Idiom Matching (Greedy Phrase Search)
Checks `lib/phrase-intent-rules.js` for non-literal phrases.
- `"kal scene kya hai"` → `"What's the plan tomorrow"`

### Layer 3: Compound Verbs
Groups multi-word Hindi verbs into single atomic English units.
- `"aa raha hu"` → `"coming"`
- `"ho gaya"` → `"done"`

### Layer 4: Contextual Disambiguation
Checks `lib/contextual-disambiguation.js` to resolve ambiguous words using a ±3 token window.
- `"kal"` (near past-tense verb like `tha`) → `"yesterday"`
- `"kal"` (near future verb like `milte`) → `"tomorrow"`

### Layer 5: Dictionary Token Lookup & Levenshtein Fuzzy Match
Translates remaining words using `dictionary.json`. Falls back to Levenshtein distance matching for slight misspellings (`bhook` → `bhuk`).

### Layer 6: Advanced Regex Grammar (SOV → SVO)
Indian languages use Subject-Object-Verb order. `lib/grammar-rules.js` natively restructures sentences into English SVO format using generic regex boundaries.
- `"train kab aayega"` → `"When will the train come?"`
- `"tu ghar ja"` → `"You go home."`

### Layer 7: Formatting & Vocative Commas
Cleans up punctuation and automatically formats vocative addresses.
- `"bro kaise ho"` → `"Bro, how are you?"`

### 🏆 Output Scoring Engine
`lib/scoring-engine.js` analyzes the engine's path and attaches confidence scores:
- `exact_match`, `smart_guess`, `typo_fixed`, `partial`

---

## 4. Why MutationObserver Is NOT Needed

React's controlled component pattern (`value` + `onChange`) guarantees that **every** user interaction — typing, pasting, deleting, clearing — fires the `onChange` handler, which updates React state, which triggers `useEffect`. 

**MutationObserver** watches DOM mutations, but React state changes happen *before* the DOM updates. Using MutationObserver in a React app would create a redundant, out-of-sync observation layer. 

The correct approach is `useEffect` with proper dependencies: `[debouncedText, source, target, isDictReady]`.

---

## 5. Real-Time Translation Flow

Translation fires on **every** change:

| Trigger | How It Works |
|---------|-------------|
| User types | `onChange` → `setInputText` → `useDebounce(200ms)` → `useEffect` → translate |
| Swap click | `handleSwap` → swaps state → `useEffect` → translate |
| Clear click | `setInputText('')` → `useEffect` → clears output |

**200ms debounce** balances responsiveness and performance.

---

## 6. File Structure

```
public/
├── dictionary.json              # 1.2MB optimized word + phrase dictionary
├── sw.js                        # Service Worker (Network-First for PWA)

lib/
├── dictionary-engine.js         # Main 7-Layer orchestrator
├── grammar-rules.js             # Layer 6: SOV -> SVO Regex engine
├── phrase-intent-rules.js       # Layer 2 & 3: Idioms and Compound Verbs
├── contextual-disambiguation.js # Layer 4: Context windowing
├── typo-map.js                  # Layer 1: Chat slang normalization
├── scoring-engine.js            # Confidence scoring metric generator
├── tier-router.js               # Legacy routing reference
└── languages.js                 # Language pairs config

scripts/
└── build-dictionary.js          # Generator to compile public/dictionary.json

tests/
└── test-engine.js               # Core unit test suite ensuring engine accuracy

hooks/
├── useTranslation.js            # React hook bridging UI and the Engine
└── useDebounce.js               # Performance utility

app/
└── components/translator/       # UI Components

docs/
├── 09-app-vision-and-goals.md   # This document
├── dictionary_schema_upgrade.md # Technical doc on the JSON swap
└── 10-ml-model-roadmap.md       # Roadmap for transitioning to ML
```

---

## 7. Performance

| Metric | Target | Achieved |
|--------|--------|----------|
| Dictionary load | < 200ms | **~50ms** |
| Translation latency | < 50ms | **< 5ms** (in-memory + offline) |
| UI freeze | None | **None** |
| Engine Tests | 100% | **19/19 complex conversational scenarios pass** |

---

## 8. Next Steps

### Phase 1: Dictionary Expansion
- Index the v3 100k dataset (currently only using v1 + v2).
- Add more individual Marlish words for better word-level coverage.

### Phase 2: Custom Machine Learning (Transformer) Model
- The absolute endgame for perfect grammar translation.
- Generate a Parallel Sentence Corpus from our dictionary.
- Fine-tune a lightweight Seq2Seq Transformer model.
- Export to ONNX and deploy inside the browser via WebAssembly (`Transformers.js`).
- *See `docs/10-ml-model-roadmap.md` for the full technical breakdown.*

### Phase 3: Community
- Crowdsource corrections.
- User-submitted phrases.
- Regional dialect support (Mumbaikar Hinglish vs UP Hinglish).
