# 🔄 Marlish.AI — Strategic Pivot Analysis & Implementation Plan

**Prepared for:** Shreyas (Collaborator) & Sanket (Project Owner)  
**Date:** May 2026  
**Status:** Pre-implementation — Awaiting Sign-off  
**Context:** mT5-small scratch training yielded BLEU ~3. This document analyses the proposed pivot, identifies what to keep vs. discard, and lays out a concrete implementation plan.

---

## Table of Contents

1. [Where We Are Right Now — Honest Assessment](#1-where-we-are-right-now--honest-assessment)
2. [What Is Working and Must Be Kept](#2-what-is-working-and-must-be-kept)
3. [What Is Broken and Must Be Abandoned](#3-what-is-broken-and-must-be-abandoned)
4. [Shreyas's Proposed Pivot — What He Gets Right](#4-shreyass-proposed-pivot--what-he-gets-right)
5. [Shreyas's Proposed Pivot — The Real Problems](#5-shreyass-proposed-pivot--the-real-problems)
6. [The Browser vs. API Hosting Decision](#6-the-browser-vs-api-hosting-decision)
7. [The Recommended Architecture](#7-the-recommended-architecture)
8. [Phase-by-Phase Implementation Plan](#8-phase-by-phase-implementation-plan)
9. [Revised Project Folder Structure](#9-revised-project-folder-structure)
10. [What to Tell Recruiters](#10-what-to-tell-recruiters)

---

## 1. Where We Are Right Now — Honest Assessment

After the training run, the results are:

| What We Attempted | What We Got | Verdict |
|---|---|---|
| Fine-tune `google/mt5-small` on 18.4M pairs | BLEU ~3 | Unusable for demo |
| 40–60 hours of GPU training time | Model produces near-gibberish | Time partially wasted |
| Offline-first browser architecture | Dictionary engine works well | Keep this |
| 8-Layer rule-based NLP engine | Handles ~80% of common inputs | Keep and refine |
| 18.4M bidirectional training pairs | Dataset exists and is structured | Partially reusable |

**The core problem in one sentence:**  
Training a high-quality translation model from scratch requires either (a) a perfectly curated, massive dataset, or (b) years of research infrastructure. We have neither. BLEU ~3 is not a dataset size problem — it is a fundamental mismatch between what we expected fine-tuning to do and what it actually requires.

Continuing to train mT5-small further on the same data will not meaningfully improve BLEU. The ceiling with this data and this approach is approximately BLEU 5–7 after full training. That still produces broken, unusable output.

**Shreyas's pivot direction is correct. The execution plan needs significant revision.**

---

## 2. What Is Working and Must Be Kept

Before cutting anything, be clear about what is genuinely strong. Throwing away working code is as bad a mistake as keeping broken code.

### ✅ The 8-Layer Rule-Based NLP Engine (`lib/`)

This is the most underrated part of the project. It handles the hardest problems in Indian chat language:

- Typo normalization: `kr` → `kar`, `rha` → `raha`
- Full-sentence idiom matching: `kya scene hai` → `What's the plan?`
- Contextual disambiguation: `kal` → `yesterday` or `tomorrow` based on verb tense
- SOV → SVO grammar reordering
- Compound verb detection: `ja raha hu` as a single semantic unit
- Confidence scoring that knows when it is uncertain

This engine translates **< 5ms**, works **100% offline**, requires **zero download**, and handles the majority of casual Hinglish/Marlish chat that any demo will actually show. It is a real technical achievement and should not be touched unless a specific layer is proven to be wrong.

### ✅ The Offline-First PWA Architecture

The Service Worker + IndexedDB caching architecture means the app loads and works without internet after the first visit. This is a genuine UX differentiator over every cloud-based translator. Keep it.

### ✅ The 18.4M Pair Dataset

Even if it cannot train a seq2seq model to useful BLEU scores, this dataset has real value:
- It can be used to build and validate the transliteration dictionary
- It is evidence of serious data engineering work for the portfolio
- Subset of it (the curated 100K conversational pairs) can benchmark the new pipeline

### ✅ The Adaptive Debounce + Tier Router Architecture

The idea of routing easy inputs to a fast rule engine and hard inputs to a heavier ML layer is architecturally correct. The tier router concept stays. Only the Tier 2 implementation changes.

### ✅ The Compiled `dictionary.json`

1.2MB, O(1) hash lookup, covers thousands of Hinglish/Marlish phrases. This is the backbone of Tier 1 and needs no changes.

---

## 3. What Is Broken and Must Be Abandoned

### ❌ The mT5-small From-Scratch Training Pipeline

**Why abandon it:**
- BLEU ~3 after training is not recoverable with more time on the same data
- The dataset, while large, contains noisy, machine-generated pairs that confuse seq2seq training
- The model has no meaningful understanding of Marlish — it sees it as noise
- 40+ more GPU hours will yield BLEU 5–7 at best — still unusable

**What to delete:**
- `scripts/train_model.py` — no longer needed
- `scripts/data_preprocessing.py` — no longer needed for ML training (keep for reference)
- `scripts/combine_datasets.py` — no longer needed for ML training
- `scripts/evaluate_model.py` — replace with new evaluation script for the new pipeline
- `docs/Dictionary_Refs/ml_splits/` — 18.4M row split files (free up disk space; keep source CSVs)
- `models/marlish_mt5_finetuned/` — delete checkpoint files (large, no longer useful)

**What to keep:**
- The dataset source files (CSVs, Parquets) — useful for transliteration dictionary building
- `scripts/export_onnx.py` — modify and reuse for the new model export

### ❌ The 7-Layer vs. 8-Layer Confusion in Documentation

The codebase and documentation are inconsistent — some files say 7 layers, others say 8. This creates confusion for collaborators. The actual implementation has 8 layers. Fix all documentation to say 8 consistently. This is a documentation debt, not a code problem.

### ❌ The Overly Optimistic ML Timeline Estimates

The `progress_tracker.md` and `COLLABORATION.md` contain timelines that are now invalid (e.g., "Model training: 2026-05-05"). These need to be wiped and replaced with the new plan's timeline after this pivot is approved.

---

## 4. Shreyas's Proposed Pivot — What He Gets Right

To be fair before being critical:

**Point 1 — BLEU ~3 is a dead end.** Correct. This is not a "train longer" problem. The architecture of trying to teach a small transformer Marlish from scratch without massive clean parallel data cannot produce usable output.

**Point 2 — Pre-trained models are the right direction.** Correct. IndicTrans2 and Helsinki opus-mt were trained by research teams on billions of tokens. We cannot replicate that. Using their weights as a foundation is not "giving up" — it is the professional engineering decision.

**Point 3 — The transliteration pipeline is the genuine novel contribution.** Correct. Every serious NLP researcher knows opus-mt and IndicTrans2 exist. What they haven't built is the Marlish → Devanagari preprocessing layer that makes those models work for Indian chat language. That is the actual gap this project fills.

**Point 4 — The portfolio story is stronger.** Correct. "I identified a failure mode in state-of-the-art translation models for code-mixed input and engineered a preprocessing pipeline to fix it" is a far more mature narrative than "I tried to train a model and it didn't work great."

---

## 5. Shreyas's Proposed Pivot — The Real Problems

These are not minor concerns. Each one can sink the approach if not addressed upfront.

---

### Problem 1: The Transliteration Pipeline Is the Hardest Part, Not a Phase 2 Afternoon Task

Shreyas's plan treats "build a Marlish → Devanagari transliterator" as a quick Phase 2 step. It is not. It is actually the hardest unsolved problem in this entire project — and it was the hard problem in the original approach too.

**Consider what `"udya kay scene ahe"` actually requires:**

| Token | Challenge | Naive Output | Correct Output |
|---|---|---|---|
| `udya` | Phonetic mapping | उद्या ✅ | उद्या |
| `kay` | Ambiguous — exists in both Hinglish and Marlish | काय or क्या? | काय (Marlish context) |
| `scene` | English loanword embedded in Marathi sentence | सीन or scene? | scene (pass-through) |
| `ahe` | Phonetic variant — also spelled `aahe`, `aye` | आहे ✅ | आहे |

A production-quality Marlish → Devanagari transliterator must handle:

- **Phonetic variance:** `ghar`, `ghar`, `ghur`, `ghr` all mean the same thing
- **English loanwords:** keep `party`, `scene`, `bro` as-is vs. transliterate them
- **Hinglish/Marlish disambiguation:** `kay` means different things in each language
- **Regional spelling variants:** `ahe` / `aahe` / `aye` (regional Marathi dialects)
- **Unknown tokens:** words with no clean Devanagari mapping

**If this step is weak, it poisons everything downstream.** A bad transliterator feeding a great model produces bad output. The model quality is irrelevant if the input is wrong.

**The unanswered question:** What is the actual transliteration approach?  
- **Pure rule-based?** Same brittleness problem as the original dictionary engine. Fast to build, breaks on edge cases.  
- **`indic-trans` or `aksharamukhi` library?** Viable, but needs validation on WhatsApp-style Marlish specifically — these libraries were built for formal text.  
- **Building a custom phoneme-to-grapheme mapping?** Correct approach but realistically 1–2 weeks of work, not 1 day.

**Before Phase 1 starts, Shreyas must state which approach he plans to use.**

---

### Problem 2: IndicTrans2 Cannot Run in the Browser — The Numbers Don't Add Up

Shreyas presents IndicTrans2 and opus-mt as comparable options and says "test both, pick the winner."

The reality:

| Model | Parameters | After INT8 Quantization | Browser-deployable? |
|---|---|---|---|
| IndicTrans2 (smallest) | 200M+ | ~150–200MB | ❌ No — 4–5x over budget |
| opus-mt (Helsinki) | 74M | ~40–75MB | ✅ Borderline yes |
| mT5-small (current) | 300M | ~80–100MB quantized | ❌ Already too large |

The hard browser constraint for Marlish.AI is **< 40–75MB** to avoid killing mobile users on data. IndicTrans2 blows past this by 3–4x.

This means one of two things is true, and Shreyas needs to pick one explicitly:

**Option A:** opus-mt is the browser model. IndicTrans2 is tested only to establish a quality ceiling. The choice is already made by the size constraint — Phase 1 "picking a winner" is a formality.

**Option B:** We drop the browser-offline requirement and host the model via API. This is a much bigger architectural change than a bullet point in a proposal. (See Section 6 for the full API vs. browser analysis.)

**Neither option is wrong. But pretending both models are viable browser candidates is incorrect and will waste Phase 1 testing time.**

---

### Problem 3: The Real-World BLEU for the Pipeline Will Be Lower Than Advertised

opus-mt's BLEU 15–20 is measured on clean, formal Marathi Devanagari → English benchmarks (like FLORES or WAT). The moment you add the transliteration step, you introduce error propagation.

**Error chain:**

```
Marlish input (noisy)
    → Transliterator (imperfect, ~85–90% accuracy on clean inputs)
    → Devanagari output with 10–15% token errors
    → opus-mt (trained on clean Devanagari)
    → Translation degraded by input errors
    → Real BLEU: ~10–14
```

BLEU 10–14 is still **3–5x better than our current ~3**. It is absolutely usable for a demo. But the portfolio pitch of "high quality translation" needs to be honest about this. If your demo video shows broken translations on common phrases, it undermines the entire claim.

**The mitigation:** Invest heavily in the transliteration step quality. Every percentage point of improvement there compounds directly into translation quality. The transliterator is the leverage point of the whole system.

---

### Problem 4: The "3 Days / 21 Hours" Timeline is Dangerously Optimistic

Breaking it down honestly:

| Shreyas's Phase | His Estimate | Realistic Estimate | Bottleneck |
|---|---|---|---|
| Phase 1: Test pre-trained models | 0.5 days | 0.5 days ✅ | Straightforward |
| Phase 2: Build transliteration pipeline | 0.5 days | **3–5 days** ❌ | This is the hard problem |
| Phase 3: ONNX export | 0.5 days | 1 day | Usually smooth but has edge cases |
| Phase 4: JS browser integration | 1 day | 1–2 days | Transformers.js has quirks |
| Phase 5–6: Benchmarking + demo | 0.5 days | 1 day | Fine |
| **Total** | **3 days** | **7–10 days** | |

Plan for 7–10 days. If it takes 3, great. If it takes 10, you won't be stuck mid-project with broken promises.

---

## 6. The Browser vs. API Hosting Decision

This is the most important architectural decision in the pivot and it was completely glossed over in Shreyas's proposal. It needs a clear answer before any code is written.

### Option A: Keep the Browser-Only Offline Model (opus-mt via Transformers.js)

**How it works:**  
User opens the app → on first Tier 2 trigger, browser downloads ~40–75MB ONNX model → caches in IndexedDB → all subsequent inference runs locally with zero network calls.

**Pros:**
- Preserves the core Marlish.AI offline-first differentiator
- Zero inference cost forever after the initial download
- Privacy-preserving: user's text never leaves their device
- Works on a plane, in a 2G zone, anywhere

**Cons:**
- opus-mt only (IndicTrans2 is too large)
- First-time download of 40–75MB is painful on slow mobile data
- WebAssembly inference is slower than native Python (500–1500ms per translation)
- Model is static — cannot be updated without user re-downloading

**Best for:** A portfolio demo that prioritizes the privacy + offline story. opus-mt quality (real-world BLEU ~10–14 with transliteration) is sufficient to impress.

---

### Option B: Host the Model as a Lightweight API (Recommended for Quality)

**How it works:**  
User types → browser sends text to a hosted API endpoint → Python server runs transliteration + IndicTrans2 → returns translation → browser renders result.

**Pros:**
- Unlocks IndicTrans2 (BLEU 25–35) — dramatically better quality
- No download for the user at all — app stays at ~1.2MB
- Model can be updated server-side without any client changes
- Faster inference (GPU server vs. browser WASM)

**Cons:**
- Requires internet connection (breaks offline story)
- Hosting costs money (small, but real)
- API latency adds ~200–500ms per call depending on server location
- Privacy: user text goes to your server

**Hosting options (realistic for a student/solo project):**

| Platform | Cost | GPU | Cold Start | Verdict |
|---|---|---|---|---|
| Hugging Face Inference API (free tier) | Free | Shared CPU | ~5–10s cold start | Good for demo; too slow for real use |
| Hugging Face Spaces (Gradio/FastAPI) | Free | T4 GPU (limited) | ~10–30s cold start | Good for portfolio link |
| Railway / Render (small VM) | ~$5–10/month | CPU only | Warm always | Reliable; opus-mt works fine on CPU |
| Google Cloud Run | ~$0–5/month | CPU | ~2–5s cold start | Scalable; pay per request |
| Self-hosted VPS (Hetzner/DigitalOcean) | ~$4–6/month | CPU | Warm always | Best value for a running demo |

---

### Option C: Hybrid (Recommended — Best of Both Worlds)

**How it works:**

```
User Input
    │
    ▼
Tier 1: 8-Layer Rule Engine (always, < 5ms, offline)
    │
    ├── Confidence >= 0.7 → Return result immediately (no network call)
    │
    └── Confidence < 0.7 → Tier 2:
            │
            ├── IF online → Call hosted API (IndicTrans2, BLEU 25–35)
            │
            └── IF offline → Load cached opus-mt ONNX from IndexedDB
                             (downloaded lazily on first use, ~40–75MB)
```

**Why this is best:**
- Online users get IndicTrans2 quality
- Offline users still get opus-mt quality (far better than BLEU ~3)
- The rule engine handles 80%+ of casual chat — API calls are rare
- The offline fallback means the app never fully breaks
- API costs stay near zero because most requests never reach Tier 2

**This is the architecture we recommend implementing.**

---

## 7. The Recommended Architecture

```
┌─────────────────────────────────────────────────┐
│                   USER INPUT                    │
│         (Hinglish / Marlish / Hindi / Marathi)  │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Adaptive Debounce    │  300–800ms based on input length
         │  (useAdaptiveDebounce)│
         └──────────┬────────────┘
                    │
                    ▼
         ┌───────────────────────┐
         │   TIER 1 (Always)     │  < 5ms — offline — no network
         │   8-Layer Rule Engine │  Handles ~80% of inputs
         │   + Dictionary Lookup │
         └──────────┬────────────┘
                    │
           Confidence >= 0.7?
          YES ◄─────┴─────► NO
           │                  │
    Return result         TIER 2 NEEDED
    to UI instantly            │
                    ┌──────────┴──────────┐
                    │  Transliteration    │  Marlish → Devanagari
                    │  Pipeline           │  (new core component)
                    └──────────┬──────────┘
                               │
              ┌────────────────┴───────────────┐
              │        Online?                 │
        YES ◄─┴──────────────────────► NO      │
         │                                     │
         ▼                                     ▼
┌──────────────────┐               ┌──────────────────────┐
│  Hosted API      │               │  Cached opus-mt ONNX │
│  (IndicTrans2)   │               │  (IndexedDB, ~40–75MB│
│  BLEU ~25–35     │               │  lazy downloaded)    │
│  ~200–400ms      │               │  BLEU ~10–14         │
└────────┬─────────┘               └──────────┬───────────┘
         │                                    │
         └──────────────┬─────────────────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │   Output Beautifier  │
             │   (Layer 8, always)  │
             └──────────┬───────────┘
                        │
                        ▼
                  FINAL OUTPUT
```

---

## 8. Phase-by-Phase Implementation Plan

Total estimated time: **8–12 days** (honest estimate, not 3 days).

---

### Phase 0: Cleanup & Codebase Reset (Day 1 — ~3 hours)

Before writing a single line of new code, clean the project. Working in a messy codebase causes mistakes.

**Delete the following:**

```bash
# Remove obsolete ML training scripts
rm scripts/train_model.py
rm scripts/combine_datasets.py
rm scripts/data_preprocessing.py

# Remove huge dataset split files (keep source CSVs)
rm -rf docs/Dictionary_Refs/ml_splits/

# Remove failed model checkpoints
rm -rf models/marlish_mt5_finetuned/

# Keep these:
# scripts/export_onnx.py     (modify and reuse)
# scripts/evaluate_model.py  (rewrite for new pipeline)
# scripts/build-dictionary.js (unchanged)
# All source CSVs and Parquet files in docs/Dictionary_Refs/
```

**Fix documentation inconsistencies:**
- Search every `.md` file for "7-layer" and replace with "8-layer"
- Update `progress_tracker.md` — wipe old ML training milestones, add new plan
- Update `COLLABORATION.md` with new setup instructions (no training required)

**Update `.gitignore`:**

```gitignore
# Large model files — never commit these
models/
*.bin
*.safetensors
*.onnx
*.pt

# Dataset splits (too large for git)
docs/Dictionary_Refs/ml_splits/
docs/Dictionary_Refs/*.parquet

# Python environment
venv/
__pycache__/
*.pyc

# Environment variables
.env.local
.env
```

**Deliverable:** Clean repository, no dead code, no misleading documentation.

---

### Phase 1: Test Pre-Trained Models & Pick the Stack (Day 1–2 — ~4 hours)

**Goal:** Determine which model delivers the best quality within the size and latency constraints.

**Step 1: Install test dependencies**

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install transformers sentencepiece torch indic-transliteration
```

**Step 2: Run the evaluation script**

Create `scripts/test_pretrained_models.py`:

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Test sentences — these are the benchmark for model selection
TEST_SENTENCES = [
    # (marlish_input, expected_english_output)
    ("udya kay scene ahe",         "What's the plan for tomorrow?"),
    ("ghar ye bhai",               "Come home, bro."),
    ("mi college la jato ahe",     "I am going to college."),
    ("kadhi bhetel re tu",         "When will you meet?"),
    ("jevla ka nahi",              "Did you eat or not?"),
    ("kasa ahes mitra",            "How are you, friend?"),
    ("khup busy aahe mi aata",     "I am very busy right now."),
    ("party ahe kal ratra",        "There is a party tomorrow night."),
]

def transliterate_to_devanagari(text: str) -> str:
    """
    Placeholder — Phase 2 will replace this with a proper pipeline.
    For now, use basic indic-transliteration as a baseline test.
    """
    tokens = text.split()
    result = []
    for token in tokens:
        try:
            deva = transliterate(token, sanscript.ITRANS, sanscript.DEVANAGARI)
            result.append(deva)
        except:
            result.append(token)  # passthrough English loanwords
    return " ".join(result)

def test_model(model_name: str, sentences: list):
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"{'='*60}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    for marlish, expected in sentences:
        devanagari = transliterate_to_devanagari(marlish)
        inputs = tokenizer(devanagari, return_tensors="pt", padding=True)
        outputs = model.generate(**inputs, max_new_tokens=64)
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(f"\n  Marlish:     {marlish}")
        print(f"  Devanagari:  {devanagari}")
        print(f"  Translation: {translation}")
        print(f"  Expected:    {expected}")

# Test both candidates
test_model("Helsinki-NLP/opus-mt-mr-en", TEST_SENTENCES)

# Note: IndicTrans2 test requires separate setup — see IndicTrans2 docs
# test_model("ai4bharat/indictrans2-indic-en-dist-200M", TEST_SENTENCES)
```

```bash
python scripts/test_pretrained_models.py
```

**What to look for:**
- Does the output make semantic sense (even if not perfect)?
- Are common nouns and verbs translated correctly?
- Does the model handle English loanwords (`party`, `scene`) without transliterating them?

**Decision criteria:**

| Scenario | Decision |
|---|---|
| opus-mt output is readable and mostly correct | Use opus-mt for both online and offline tiers |
| opus-mt output is broken on > 50% of test sentences | Investigate IndicTrans2 API-only approach |
| Transliteration quality is the bottleneck (not the model) | Invest Phase 2 time in transliteration, not model switching |

**Deliverable:** Test results logged. Model choice confirmed. Transliteration quality gap identified.

---

### Phase 2: Build the Marlish Transliteration Pipeline (Days 2–6 — ~4–6 days)

**This is the hardest phase. Do not underestimate it.**

The transliterator is the leverage point of the entire system. Every hour invested here compounds into translation quality improvement. A weak transliterator cannot be rescued by a better model.

**Architecture of the transliteration pipeline:**

```
Marlish Input: "udya kay scene ahe bro"
       │
       ▼
Step 1: Normalize (typo-map)
       "udya kay scene ahe bro"
       │
       ▼
Step 2: Tokenize
       ["udya", "kay", "scene", "ahe", "bro"]
       │
       ▼
Step 3: Classify each token
       udya  → MARLISH_WORD (transliterate)
       kay   → MARLISH_WORD (transliterate, context: Marlish sentence)
       scene → ENGLISH_LOANWORD (pass through)
       ahe   → MARLISH_WORD (transliterate)
       bro   → ENGLISH_LOANWORD (pass through)
       │
       ▼
Step 4: Transliterate MARLISH_WORD tokens
       udya  → उद्या
       kay   → काय
       ahe   → आहे
       │
       ▼
Step 5: Reconstruct mixed output
       "उद्या काय scene आहे bro"
       │
       ▼
Feed to translation model
```

**Step 2a: Build the token classifier**

Create `scripts/transliterator/token_classifier.py`:

```python
# English word detection (keep as-is)
ENGLISH_PASSTHROUGH = {
    "bro", "yaar", "scene", "party", "chill", "done", "ok", "okay",
    "bye", "hi", "hello", "please", "thanks", "sorry", "yes", "no"
    # Expand this list from your existing dictionary JSON
}

def classify_token(token: str, context: list) -> str:
    """
    Returns: 'ENGLISH' | 'MARLISH' | 'HINDI' | 'DEVANAGARI' | 'NUMERIC'
    """
    if token.isdigit():
        return 'NUMERIC'
    if any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in token):
        return 'DEVANAGARI'  # already in Devanagari, pass through
    if token.lower() in ENGLISH_PASSTHROUGH:
        return 'ENGLISH'
    # Default: assume Marlish romanized
    return 'MARLISH'
```

**Step 2b: Build the phoneme-to-grapheme mapping**

This is the core of the transliteration step. Use the existing dataset to build a frequency-ranked mapping:

```python
# marlish_to_devanagari_map.py
# Built from the 3.6M Marlish parquet data — most frequent romanizations win

MARLISH_MAP = {
    # High-confidence direct mappings
    "udya":  "उद्या",
    "aaj":   "आज",
    "kal":   "काल",
    "ghar":  "घर",
    "mi":    "मी",
    "tu":    "तू",
    "tya":   "त्या",
    "ahe":   "आहे",
    "aahe":  "आहे",  # variant
    "aye":   "आहे",  # regional variant
    "nahi":  "नाही",
    "nai":   "नाही",  # variant
    "kay":   "काय",
    "kasa":  "कसा",
    "kashi": "कशी",
    "ho":    "हो",
    "hoy":   "होय",
    "mitra": "मित्र",
    "bhet":  "भेट",
    # ... expand from dataset
}

# Phonetic fallback rules for unknown tokens
PHONEME_RULES = [
    ("aa", "आ"), ("ii", "ई"), ("oo", "ऊ"),
    ("sh", "श"), ("ch", "च"), ("kh", "ख"),
    ("gh", "घ"), ("jh", "झ"), ("th", "थ"),
    ("dh", "ध"), ("ph", "फ"), ("bh", "भ"),
    # ... complete phoneme table
]
```

**Step 2c: Extract the mapping from your existing dataset**

```python
# scripts/build_transliteration_map.py
# Uses the 3.6M Marlish parquet to find high-frequency romanized → Devanagari pairs

import pandas as pd
from collections import Counter

df = pd.read_parquet("docs/Dictionary_Refs/Apni_Bhasha_Marlish_Dataset.parquet")
# This dataset has romanized Marlish and standard Marathi side by side
# Extract word-level pairs and rank by frequency
# High-frequency pairs → high-confidence mappings
```

**This is why keeping the source dataset files matters** — they are the training data for the transliterator even when they aren't training data for an ML model.

**Step 2d: Handle the hard cases**

Document these explicitly and build test cases for each:

| Hard Case | Example | Strategy |
|---|---|---|
| English loanwords | `scene`, `party`, `chill` | Whitelist passthrough dictionary |
| Hinglish vs Marlish ambiguity | `kay` (Hinglish: nothing / Marlish: what) | Language detection from context |
| Regional spelling variance | `ahe` / `aahe` / `aye` | Map all variants to same Devanagari |
| Unknown token | `bhaari` (not in map) | Phoneme rule fallback → best guess |
| Fully English sentence | `what is happening` | Skip transliteration, pass as-is |

**Deliverable:** `scripts/transliterator/` module, tested against 50+ real Marlish sentences with documented accuracy rate.

---

### Phase 3: ONNX Export for Browser Offline Fallback (Day 6–7 — ~1 day)

**Goal:** Convert opus-mt to a browser-runnable ONNX file for the offline fallback path.

```bash
pip install optimum[onnxruntime] onnx onnxruntime
```

Modify `scripts/export_onnx.py` for opus-mt:

```python
from optimum.onnxruntime import ORTModelForSeq2SeqLM
from transformers import AutoTokenizer

MODEL_NAME = "Helsinki-NLP/opus-mt-mr-en"
OUTPUT_DIR = "models/onnx/opus-mt-mr-en/"

# Export to ONNX
model = ORTModelForSeq2SeqLM.from_pretrained(MODEL_NAME, export=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Export complete. Files saved to:", OUTPUT_DIR)
```

**Apply INT8 quantization:**

```python
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from optimum.onnxruntime import ORTQuantizer

quantizer = ORTQuantizer.from_pretrained(OUTPUT_DIR)
qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)
quantizer.quantize(save_dir=OUTPUT_DIR + "quantized/", quantization_config=qconfig)
```

**Copy to public directory:**

```bash
cp -r models/onnx/opus-mt-mr-en/quantized/ public/models/opus-mt-mr-en/
```

**Size check:**

```bash
du -sh public/models/opus-mt-mr-en/
# Target: < 75MB total
```

**Deliverable:** Quantized ONNX files in `public/models/`, size verified.

---

### Phase 4: Set Up the Hosted API (Day 7–8 — ~1 day)

**Goal:** Deploy IndicTrans2 (or high-quality opus-mt) as a lightweight API for the online Tier 2 path.

**Recommended: Hugging Face Spaces (Free, GPU)**

Create `api/app.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import sys
sys.path.append("scripts/")
from transliterator.pipeline import MarlishtoPipeline

app = FastAPI()
transliterator = MarlishtoPipeline()

# Load model (opus-mt for CPU; swap for IndicTrans2 if GPU available)
MODEL_NAME = "Helsinki-NLP/opus-mt-mr-en"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

class TranslationRequest(BaseModel):
    text: str
    direction: str = "marlish_to_english"

class TranslationResponse(BaseModel):
    translation: str
    devanagari_intermediate: str
    model_used: str
    latency_ms: float

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    import time
    start = time.time()

    # Step 1: Transliterate Marlish → Devanagari
    devanagari = transliterator.to_devanagari(request.text)

    # Step 2: Translate
    inputs = tokenizer(devanagari, return_tensors="pt", padding=True)
    outputs = model.generate(**inputs, max_new_tokens=128)
    translation = tokenizer.decode(outputs[0], skip_special_tokens=True)

    latency = (time.time() - start) * 1000

    return TranslationResponse(
        translation=translation,
        devanagari_intermediate=devanagari,
        model_used=MODEL_NAME,
        latency_ms=round(latency, 2)
    )

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Deploy to Hugging Face Spaces:**

```bash
# Create a new Space at huggingface.co/spaces
# Choose FastAPI template
# Upload api/app.py and requirements
# Set hardware to CPU Basic (free) or T4 GPU (paid)
```

**Your API endpoint will be:**
```
https://YOUR_USERNAME-marlish-api.hf.space/translate
```

**API call from the browser (in `lib/tier-router.js`):**

```javascript
async function callHostedAPI(text, direction = 'marlish_to_english') {
  const response = await fetch('https://YOUR_USERNAME-marlish-api.hf.space/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, direction })
  });
  const data = await response.json();
  return {
    text: data.translation,
    confidence: 0.9,
    label: 'ml_translation',
    latency_ms: data.latency_ms,
    model: data.model_used
  };
}
```

**Deliverable:** Live API endpoint, tested from browser, response time < 500ms.

---

### Phase 5: Browser Integration & Tier Router Update (Day 8–9 — ~1.5 days)

**Goal:** Wire everything into `lib/tier-router.js` so the full hybrid pipeline works seamlessly in the browser.

**Updated `lib/tier-router.js`:**

```javascript
import { runDictionaryEngine } from './dictionary-engine.js';
import { transliterateToDevanagari } from './transliterator.js';

const API_ENDPOINT = process.env.NEXT_PUBLIC_API_ENDPOINT;
const CONFIDENCE_THRESHOLD = 0.70;
let onnxModel = null;

export async function routeTranslation(text, direction) {
  // TIER 1: Always run first — fast, offline, no network
  const tier1Result = await runDictionaryEngine(text, direction);

  if (tier1Result.confidence >= CONFIDENCE_THRESHOLD) {
    return { ...tier1Result, tier: 1 };
  }

  // TIER 2: Low confidence — try ML
  const devanagari = transliterateToDevanagari(text);

  // Online path: call hosted API (better model)
  if (navigator.onLine && API_ENDPOINT) {
    try {
      const apiResult = await callHostedAPI(devanagari, direction);
      return { ...apiResult, tier: 2, path: 'api' };
    } catch (err) {
      console.warn('API unavailable, falling back to ONNX:', err);
    }
  }

  // Offline path: use cached ONNX model
  const onnxResult = await runOnnxInference(devanagari);
  return { ...onnxResult, tier: 2, path: 'onnx' };
}

async function runOnnxInference(devanagariText) {
  if (!onnxModel) {
    // Lazy load — only on first Tier 2 offline call
    const { pipeline } = await import('@xenova/transformers');
    onnxModel = await pipeline('translation', 'models/opus-mt-mr-en/', {
      quantized: true
    });
  }
  const result = await onnxModel(devanagariText, { max_new_tokens: 128 });
  return {
    text: result[0].translation_text,
    confidence: 0.82,
    label: 'ml_translation',
  };
}
```

**Add transliterator to JS side (`lib/transliterator.js`):**

The JavaScript transliterator is a port of the Python mapping, compiled from the same source data. It runs client-side before any API call, meaning:
- Online path: transliterate in JS → send Devanagari to API
- Offline path: transliterate in JS → feed local ONNX model

```javascript
// Auto-generated from scripts/build_transliteration_map.py
// Do not edit manually — run `npm run build-translit` to regenerate
import MARLISH_MAP from '../public/transliteration_map.json';

export function transliterateToDevanagari(text) {
  const tokens = text.toLowerCase().trim().split(/\s+/);
  return tokens.map(token => {
    if (MARLISH_MAP[token]) return MARLISH_MAP[token];
    if (isEnglishLoanword(token)) return token;
    return applyPhonemeRules(token); // fallback
  }).join(' ');
}
```

**Deliverable:** Full hybrid pipeline working in browser. Test: type Marlish, see English. Check browser network tab to confirm API calls only fire when confidence < 0.70.

---

### Phase 6: Benchmarking, Demo & Documentation (Day 10–12 — ~1.5 days)

**Benchmark the complete pipeline:**

Create `scripts/evaluate_pipeline.py`:

```python
# Tests the full pipeline: Marlish → Transliterate → Translate
# Measures: transliteration accuracy, final BLEU, latency

TEST_SET = [
    ("udya kay scene ahe",     "What is the plan for tomorrow?"),
    ("ghar ye bhai",           "Come home, bro."),
    ("kasa ahes mitra",        "How are you, friend?"),
    # Add 50+ real WhatsApp-style Marlish sentences
]

# Run and report:
# 1. Transliteration accuracy (correct Devanagari / total tokens)
# 2. BLEU score on final translations
# 3. Average latency (API path vs. ONNX path)
# 4. Tier 1 hit rate (% of inputs handled by rule engine without ML)
```

**Expected results to target:**

| Metric | Target | Acceptable |
|---|---|---|
| Tier 1 hit rate | > 70% | > 60% |
| Transliteration accuracy | > 85% | > 75% |
| API path BLEU | > 20 | > 15 |
| ONNX path BLEU | > 10 | > 8 |
| API latency (p95) | < 400ms | < 700ms |
| ONNX first-load time | < 4s | < 8s |
| ONNX inference latency | < 800ms | < 1500ms |

**Record the demo video:**

Show these specific scenarios in the demo:
1. Common Marlish chat: `kasa ahes bhai` → instant (Tier 1, < 5ms)
2. Complex sentence: `mi aaj college la gel nahi karan khup busy hoto` → ML path
3. Offline mode: disable network, show ONNX fallback still works
4. Speed comparison: show the < 5ms counter for Tier 1 hits

**Update documentation:**

- `progress_tracker.md`: Mark old ML milestones done/abandoned, add new pipeline milestones
- `COLLABORATION.md`: Remove training instructions, add transliteration pipeline guide
- `architecture.md`: Update to reflect hybrid API + ONNX architecture
- `README.md`: New demo GIF, updated tech stack

**Deliverable:** Benchmark report, demo video, updated docs. Project is portfolio-ready.

---

## 9. Revised Project Folder Structure

```
MarlishAI/
│
├── app/                              # Next.js App Router (unchanged)
│   ├── components/
│   └── page.js
│
├── hooks/                            # React Hooks (unchanged)
│   ├── useTranslation.js
│   ├── useAdaptiveDebounce.js
│   └── useTTS.js
│
├── lib/                              # Core NLP Engine (partially updated)
│   ├── dictionary-engine.js          # Unchanged — 8-layer rule engine
│   ├── typo-map.js                   # Unchanged
│   ├── phrase-intent-rules.js        # Unchanged
│   ├── contextual-disambiguation.js  # Unchanged
│   ├── grammar-rules.js              # Unchanged
│   ├── scoring-engine.js             # Unchanged
│   ├── tier-router.js                # UPDATED — new API + ONNX routing logic
│   └── transliterator.js             # NEW — Marlish → Devanagari (JS port)
│
├── scripts/                          # Updated Python utilities
│   ├── build-dictionary.js           # Unchanged
│   ├── build_transliteration_map.py  # NEW — generates transliteration_map.json
│   ├── test_pretrained_models.py     # NEW — Phase 1 model evaluation
│   ├── export_onnx.py                # UPDATED — now exports opus-mt, not mT5
│   ├── evaluate_pipeline.py          # NEW — end-to-end pipeline benchmarking
│   └── transliterator/               # NEW — Python transliteration module
│       ├── __init__.py
│       ├── pipeline.py               # Main transliteration orchestrator
│       ├── token_classifier.py       # English vs. Marlish detection
│       └── marlish_to_devanagari_map.py  # Phoneme mapping data
│
├── api/                              # NEW — Hosted API (deployed to HF Spaces)
│   ├── app.py                        # FastAPI server
│   ├── requirements.txt              # API-specific dependencies
│   └── Dockerfile                    # For containerized deployment
│
├── models/                           # Model files (gitignored)
│   └── onnx/
│       └── opus-mt-mr-en/
│           └── quantized/            # Browser-ready ONNX files
│
├── public/                           # Static assets
│   ├── dictionary.json               # Compiled rule engine dictionary (~1.2MB)
│   ├── transliteration_map.json      # NEW — compiled Marlish→Devanagari map
│   ├── models/                       # ONNX model files (copied from models/)
│   │   └── opus-mt-mr-en/
│   └── sw.js                         # Service Worker (updated cache list)
│
├── docs/
│   ├── Dictionary_Refs/              # Source datasets (CSVs, Parquets — keep)
│   │   └── [NO ml_splits/ anymore]   # Deleted — no longer needed
│   ├── progress_tracker.md           # Updated with new milestones
│   ├── architecture.md               # Updated to reflect new architecture
│   └── COLLABORATION.md              # Updated — no training required
│
├── tests/
│   ├── test-engine.js                # Unchanged — 8-layer engine tests
│   └── test-transliterator.js        # NEW — transliteration accuracy tests
│
├── .env.local                        # API endpoint + config
├── .gitignore                        # Updated — excludes models/, splits/
└── package.json
```

**Files deleted vs. original:**

| Deleted File | Reason |
|---|---|
| `scripts/train_model.py` | mT5 scratch training abandoned |
| `scripts/data_preprocessing.py` | No longer training ML model |
| `scripts/combine_datasets.py` | No longer training ML model |
| `docs/Dictionary_Refs/ml_splits/` | 18.4M pairs no longer needed |
| `models/marlish_mt5_finetuned/` | Checkpoint files from failed run |

**Files added:**

| New File | Purpose |
|---|---|
| `scripts/transliterator/pipeline.py` | Core transliteration logic |
| `scripts/build_transliteration_map.py` | Extracts mappings from existing datasets |
| `scripts/test_pretrained_models.py` | Phase 1 model benchmarking |
| `scripts/evaluate_pipeline.py` | End-to-end quality measurement |
| `lib/transliterator.js` | Client-side JS transliterator |
| `api/app.py` | Hosted FastAPI server |
| `public/transliteration_map.json` | Compiled mapping for browser |

---

## 10. What to Tell Recruiters

**Before (weak):**
> "I tried to train a multilingual translation model on 18 million sentence pairs but the BLEU score was only 3."

**After (strong):**
> "I identified a fundamental gap in state-of-the-art Indian language translation models: they are trained on formal Devanagari text and completely fail when given romanized code-mixed input like Marlish. I engineered a transliteration preprocessing pipeline that converts noisy Marlish chat into standard Devanagari, then feeds it into Helsinki-NLP's opus-mt model. The result is a fully offline-capable browser application that achieves BLEU ~12–15 on real WhatsApp-style input — compared to BLEU ~3 from a scratch-trained model. The system uses a hybrid architecture where a fast rule engine handles 80% of inputs in under 5ms, and the ML path only activates for complex sentences."

**Key technical claims you can defend:**
- Designed and built a token classifier + phoneme-to-grapheme transliteration pipeline for Marlish → Devanagari
- Engineered the preprocessing layer that makes SOTA models work on code-mixed input they were never trained on
- Deployed ONNX-quantized model in the browser via Transformers.js with IndexedDB caching for offline use
- Built a two-tier hybrid system that maintains < 5ms latency for common inputs while providing ML-quality output for complex ones
- Benchmarked the full pipeline with BLEU scoring and latency profiling across both online (API) and offline (ONNX) paths

---

## Summary: Green Light Conditions

Give Shreyas the go-ahead for Phase 1 **only after** he answers these three questions:

1. **Which transliteration approach?** Rule-based map, `indic-transliteration` library, or custom phoneme-to-grapheme model? The answer determines whether Phase 2 takes 2 days or 2 weeks.

2. **Browser constraint still a hard requirement?** If yes, opus-mt is the production model and IndicTrans2 is tested for reference only. If no, the architecture changes significantly.

3. **What does Phase 1's test script actually measure?** It must benchmark transliteration quality separately from translation quality, or you won't know which component is the bottleneck.

These are not bureaucratic questions. They are the difference between this pivot working in 10 days or stalling for a month.

---

*This document supersedes all previous ML training plans. The `progress_tracker.md` should be updated to reflect this pivot once Phase 1 results are confirmed.*
