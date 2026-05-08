# 🤝 Marlish.AI — Collaboration Guide

Welcome to **Marlish.AI** — a real-time, offline-first Indian language intelligence system. This document is the single reference for any collaborator contributing to the project, whether you are working on the JavaScript NLP engine, the Python ML pipeline, or the React frontend.

Read this fully before touching any code. The Critical Technical Details section alone will save you hours of debugging.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Project Architecture](#2-project-architecture)
3. [How the 8-Layer Engine Works](#3-how-the-8-layer-engine-works)
4. [Full Project File Structure](#4-full-project-file-structure)
5. [Shared Collaboration Files](#5-shared-collaboration-files)
6. [Dataset Specifications](#6-dataset-specifications)
7. [Getting Started — Google Colab Pro](#7-getting-started--google-colab-pro)
8. [Getting Started — Local RTX GPU](#8-getting-started--local-rtx-gpu)
9. [Critical Technical Details](#9-critical-technical-details)
10. [Known Bugs to Fix Before Training](#10-known-bugs-to-fix-before-training)
11. [Training Strategy & Checkpoint Log](#11-training-strategy--checkpoint-log)
12. [ONNX Export & Browser Deployment](#12-onnx-export--browser-deployment)
13. [Development Tips & Workflow](#13-development-tips--workflow)
14. [Contribution Checklist](#14-contribution-checklist)
15. [Requirements Reference](#15-requirements-reference)

---

## 1. Problem Statement

Traditional translation engines (Google Translate, DeepL) are trained on formal, written corpora — news articles, books, and official documents. They break down completely when faced with how Indians actually communicate digitally.

### Four Core Failure Modes

**1. Code-Mixed Language (Hinglish / Marlish)**

Indians do not write in formal Hindi or Marathi when chatting. They mix languages mid-sentence without thinking about it — this is called code-mixing and it is the default register, not a quirk.

```
"bhai sun, kal party hai toh aaja"
→ Google: "brother listen, tomorrow party is then come"  ❌
→ Marlish.AI: "Hey bro, there's a party tomorrow — you should come."  ✅
```

**2. Phonetic Variance & Abbreviations**

There is no standard romanization for Hindi or Marathi. Every user spells phonetically and inconsistently. Common shortenings are completely unrecognized by standard engines.

```
All valid, common forms of the same word:
  kar / kr / krr / kaR / Kar     → "do"
  raha / rha / rhaa / rha        → "going/staying"
  hai / h / he / hain            → "is/are"
```

**3. Contextual Ambiguity**

High-frequency words carry multiple meanings that only context can resolve. A word-level lookup always picks wrong.

```
"kal" → "yesterday" OR "tomorrow"  (resolved by nearby verb tense)
"par" → "but" OR "on/upon"         (resolved by sentence role)
"hi"  → "only/just" OR emphasis    (resolved by position)
```

**4. SOV → SVO Structural Mismatch**

Indian languages are Subject-Object-Verb. English is Subject-Verb-Object. Naive translation produces broken, ungrammatical output.

```
Input:   "main ghar ja raha hu"    (I  home  go  am)   ← SOV
Broken:  "I home go am"                                 ❌
Fixed:   "I am going home."                             ✅
```

### The Benchmark Example

This single sentence captures all four problems at once:

```
Input:    "kal milte hai bro"

Broken:   "tomorrow/yesterday meet are brother"
           ↑ ambiguous  ↑ SOV order  ↑ wrong register

Expected: "Bro, let's meet tomorrow."
           ↑ vocative  ↑ SOV fixed  ↑ context resolved  ↑ natural tone
```

**Marlish.AI aims to:**
1. **Decode** messy, casual chat into clear, natural language
2. **Maintain Context** using an advanced multi-layered NLP pipeline
3. **Run Offline** entirely in the browser for privacy and speed
4. **Solve Grammar** issues specific to Indian SOV → English SVO structures
5. **Handle the long tail** of slang, typos, and rapidly evolving regional idioms

---

## 2. Project Architecture

Marlish.AI uses a **Two-Tier Hybrid Architecture**. The key principle: **the ML model augments the rule engine — it does not replace it.**

```
User Input
    │
    ▼
┌─────────────────────────────┐
│         TIER 1              │  < 5ms latency
│   8-Layer Rule-Based NLP    │  Handles ~80% of inputs
│   (JavaScript, in-browser)  │  O(1) dictionary lookups
└──────────────┬──────────────┘
               │
        Confidence >= 0.7?
       YES ◄───┴───► NO
        │              │
        │              ▼
        │   ┌─────────────────────────────┐
        │   │         TIER 2              │  ~200–500ms
        │   │   ML Fallback (mT5-small)   │  Handles complex sentences
        │   │   (ONNX via Transformers.js) │  only when rules fail
        │   └──────────────┬──────────────┘
        │                  │
        └──────────┬───────┘
                   │
                   ▼
           Output Beautifier
                   │
                   ▼
            Final Output
```

### Why Not Pure ML?

It is tempting to throw away the rule engine and just train a large ML model. This is a critical mistake for a browser app.

| Concern | Pure ML Only | Hybrid (Marlish approach) |
|---|---|---|
| Per-keystroke latency | 500–2000ms | < 5ms (Tier 1 handles 80%) |
| First-load size | 30–50MB+ (model required upfront) | ~1.2MB dictionary; model lazy-loaded |
| Battery drain | High (neural net on every keystroke) | Near-zero on the rule-based path |
| Hallucination risk | High (forces formal grammar) | Controlled (ML only for edge cases) |
| Offline capability | Needs cached model | Dictionary always available from load |
| Training cost | Expensive; full model from scratch | Fine-tuning only; free on Colab Pro |

---

## 3. How the 8-Layer Engine Works

The rule-based NLP engine in `lib/dictionary-engine.js` processes every input through eight ordered layers. Understanding this pipeline is essential before contributing to any `lib/` file.

### Layer Overview

```
Input Text
    │
    ▼  Layer 1: Normalization       (kr→kar, rha→raha, kyaaa→kya)
    │
    ▼  Layer 2: Intent Matching     (full sentence idiom check — short-circuits if matched)
    │
    ▼  Layer 3: Compound Verb       (ja raha hu → "am going" as a single unit)
       Assembly
    │
    ▼  Layer 4: Contextual          (kal → yesterday/tomorrow based on nearby verb)
       Disambiguation               (Levenshtein fuzzy match for near-typos)
    │
    ▼  Layer 5: Grammar Reordering  (SOV → SVO, auxiliary verb insertion)
    │
    ▼  Layer 6: Vocative Handling   ("bro where are you" → "Bro, where are you?")
    │
    ▼  Layer 7: Confidence Scoring  (0.0–1.0 score + label: exact/smart_guess/partial)
    │
    ▼  Layer 8: Beautification      (capitalize, punctuation, contraction cleanup)
    │
    ▼
  Output → Tier Router (score >= 0.7 → return | score < 0.7 → ML fallback)
```

### Layer Details

**Layer 1 — Normalization** (`typo-map.js`)
Runs before everything else. Expands abbreviations, collapses repeated characters, lowercases. This layer also runs as a preprocessor before ML inference — the model was not trained on heavily abbreviated input.

**Layer 2 — Intent Matching** (`phrase-intent-rules.js`)
Checks if the entire sentence matches a known idiom. If matched, the result is returned immediately with `confidence: 1.0` — no further processing needed. This is the fastest path through the system.

| Input | Output | Confidence |
|---|---|---|
| `kya scene hai` | `What's the plan?` | 1.0 |
| `koi baat nahi` | `No worries.` | 1.0 |
| `theek hai` | `Alright.` | 1.0 |

**Layer 3 — Compound Verb Assembly** (`phrase-intent-rules.js`)
Hindi and Marathi compound verbs (`ja raha hu`, `kha liya`, `ho jayega`) must be identified as single semantic units before word-level tokenization. The engine uses a greedy lookahead of up to 4 tokens.

**Layer 4 — Contextual Disambiguation** (`contextual-disambiguation.js`)
Uses a ±2 token context window to resolve ambiguous words. Also handles Levenshtein fuzzy matching (distance ≤ 1) for words that survive normalization but still miss the dictionary.

**Layer 5 — Grammar Reordering** (`grammar-rules.js`)
Detects SOV patterns, reorders to SVO, and inserts implied auxiliary verbs (`is`, `am`, `are`) that conversational Hinglish typically drops.

**Layer 6 — Vocative Handling** (`contextual-disambiguation.js`)
Detects address terms (`bro`, `bhai`, `yaar`, `dost`) at the start or end of a sentence, applies correct comma placement and capitalization.

**Layer 7 — Confidence Scoring** (`scoring-engine.js`)
Calculates reliability score based on match quality per token:

| Match Type | Score Impact |
|---|---|
| Full intent / phrase match | 1.0 (maximum) |
| Direct dictionary match | ~0.85–0.95 |
| Context-disambiguated match | ~0.75–0.85 |
| Fuzzy (Levenshtein ≤ 1) match | ~0.55–0.70 |
| Unknown / passthrough token | −0.20 per token |

Labels surfaced to UI: `exact_match`, `smart_guess`, `typo_fixed`, `partial`.

**Layer 8 — Beautification** (`dictionary-engine.js`)
Final pass on all output regardless of tier: capitalize first letter, fix `i` → `I`, resolve punctuation spacing, remove duplicate punctuation.

> ⚠️ **If you add a new layer**, you must add corresponding score constants to `lib/scoring-engine.js` or the confidence threshold logic will be miscalibrated.

---

## 4. Full Project File Structure

```
MarlishAI/
│
├── app/                              # Next.js App Router (React 19)
│   ├── components/                   # Reusable UI components
│   │   ├── TranslatorPanel.jsx       # Main translation UI
│   │   ├── LanguageSelector.jsx      # Source / target language picker
│   │   └── ConfidenceBadge.jsx       # Displays score + label
│   ├── layout.js                     # Root shell, metadata, SW registration
│   ├── page.js                       # Entry point — renders TranslatorPanel
│   └── globals.css                   # Tailwind v4 base styles
│
├── hooks/                            # Custom React Hooks
│   ├── useTranslation.js             # Core hook — wraps Tier Router, exposes result state
│   ├── useAdaptiveDebounce.js        # Dynamic debounce (300–800ms by input length)
│   └── useTTS.js                     # Text-to-Speech hook (Web Speech API)
│
├── lib/                              # Core 8-Layer Rule-Based NLP Engine
│   ├── dictionary-engine.js          # Primary orchestrator — runs all 8 layers
│   ├── typo-map.js                   # Layer 1: Normalization / abbreviation expansion
│   ├── phrase-intent-rules.js        # Layers 2 & 3: Intent matching + compound verbs
│   ├── contextual-disambiguation.js  # Layers 4 & 6: Context resolution + vocative
│   ├── grammar-rules.js              # Layer 5: SOV→SVO reordering + aux insertion
│   ├── scoring-engine.js             # Layer 7: Confidence score calculation
│   └── tier-router.js                # Routes to Tier 1 (dict) or Tier 2 (ML)
│
├── scripts/                          # ML Pipeline (Python) + Dictionary Builder (JS)
│   ├── build-dictionary.js           # Compiles source CSVs → public/dictionary.json
│   ├── combine_datasets.py           # Merges all data sources → Combined_Parallel_Dataset.csv
│   ├── data_preprocessing.py         # Creates bidirectional pairs, dedup, 80/10/10 split
│   ├── train_model.py                # mT5-small fine-tuning (GPU/BF16, checkpoint resume) ⚠️
│   ├── export_onnx.py                # PyTorch → ONNX → INT8 quantization
│   ├── evaluate_model.py             # BLEU evaluation per direction ⚠️
│   └── marlish_colab_training.ipynb  # Colab-ready one-click training notebook
│
├── models/                           # Trained weights and ONNX exports
│   ├── marlish_mt5_finetuned/        # PyTorch checkpoint directory
│   │   ├── checkpoint-XXXX/          # Resumable training checkpoints
│   │   └── final/                    # Best model (lowest val loss)
│   └── onnx/                         # Browser-ready ONNX files
│       ├── encoder_model_quantized.onnx
│       ├── decoder_model_quantized.onnx
│       └── tokenizer/
│
├── public/                           # Static assets served by Next.js
│   ├── dictionary.json               # Compiled runtime dictionary (~1.2MB, O(1) lookups)
│   ├── models/                       # ← Copy ONNX outputs here for browser access
│   └── sw.js                         # Service Worker (PWA offline caching)
│
├── docs/
│   ├── Dictionary_Refs/
│   │   ├── ml_splits/                # train.csv / val.csv / test.csv (18.4M pairs)
│   │   └── *.csv / *.parquet         # Source dataset files
│   ├── architecture.md               # Detailed system architecture reference
│   └── progress_tracker.md           # Single source of truth for task status
│
├── tests/
│   └── test-engine.js                # NLP engine test suite
│
├── package.json
└── requirements.txt
```

---

## 5. Shared Collaboration Files

Two ZIP files contain everything needed to start the ML pipeline.

### 📥 `ml_splits.zip`

Pre-processed and split parallel corpus. Extract to `docs/Dictionary_Refs/ml_splits/`.

| File | Rows | Purpose |
|---|---|---|
| `train.csv` | ~14.8M | Main training corpus |
| `val.csv` | ~1.85M | Validation — BLEU monitored during training |
| `test.csv` | ~1.85M | Final hold-out evaluation (do not use during training) |

Total unique pairs: **18,483,691** across 8 bidirectional translation directions.

### 📥 `scripts.zip`

The core Python training pipeline.

| File | Purpose |
|---|---|
| `train_model.py` | GPU-optimized mT5 fine-tuning with BF16 + checkpoint resume |
| `export_onnx.py` | PyTorch → ONNX → INT8 quantization for browser deployment |
| `evaluate_model.py` | Per-direction BLEU scoring on the test set |
| `marlish_colab_training.ipynb` | Colab-ready notebook — pre-wired for Drive mount + one-click training |

> ⚠️ There are **3 known bugs** in `train_model.py` and `evaluate_model.py`. Read [Section 10](#10-known-bugs-to-fix-before-training) before running any scripts.

---

## 6. Dataset Specifications

### Training Data Schema

All split files (`train.csv`, `val.csv`, `test.csv`) follow this schema:

| Column | Type | Description | Example |
|---|---|---|---|
| `source` | string | Input text in source language | `kya kr rha hai bro` |
| `target` | string | Ground truth in target language | `What are you doing, bro?` |
| `direction` | string | Task identifier (see below) | `hinglish_to_english` |

### All 8 Supported Directions

| Direction | Train Pairs | Notes |
|---|---|---|
| `marathi_to_english` | 5,795,175 | Largest direction by volume |
| `english_to_marlish` | 2,891,335 | |
| `marlish_to_english` | 2,890,500 | |
| `english_to_hinglish` | 805,093 | |
| `hinglish_to_english` | 804,872 | |
| `english_to_hindi` | 799,912 | |
| `hindi_to_english` | 799,518 | |
| `english_to_marathi` | **547** | ⚠️ Very sparse — weak reverse Marathi in v1 |

> **Note on `english_to_marathi`:** The Marathi Parquet sources only contain `src (Marathi) → tgt (English)` columns. Reverse direction data was not available. The model will have limited English → Marathi capability in v1. This is earmarked for future data collection.

### Directional Prefix Format

The model is **multi-task** — it handles all 8 directions in a single model by using task prefixes. This is mandatory. The model will produce incorrect output without them.

```
Input row format: "translate {source_lang} to {target_lang}: {source_text}"

Examples:
  "translate Hinglish to English: kal milte hai bro"
  "translate Marlish to Marathi: kadhi bhetel re"
  "translate English to Hinglish: let's meet tomorrow"
```

Prefixes are parsed automatically from the `direction` column by `train_model.py`. Do not hardcode them manually.

### Adding New Data

If you add new sentence pairs, ensure:
1. No duplicate `(source, target, direction)` triplets — run `data_preprocessing.py` to re-dedup.
2. Source text is **not** pre-normalized (raw, natural input only — normalization happens at runtime).
3. Target text is clean, natural, grammatically correct output.
4. The `direction` value matches exactly one of the 8 supported direction strings above.

---

## 7. Getting Started — Google Colab Pro

Recommended for collaborators without a local GPU. Colab Pro provides access to A100 (80GB) or V100 (16GB) GPUs — significantly faster than a local RTX 3060 for full training runs.

### Step 1: Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

Save all checkpoints to Drive. Colab sessions disconnect — anything not on Drive will be lost.

### Step 2: Upload Files

Upload `ml_splits.zip` and `scripts.zip` directly to your Drive, then copy to the Colab session:

```python
!cp /content/drive/MyDrive/MarlishAI/ml_splits.zip .
!cp /content/drive/MyDrive/MarlishAI/scripts.zip .
```

### Step 3: Extract

```python
!unzip ml_splits.zip -d docs/Dictionary_Refs/ml_splits/
!unzip scripts.zip -d scripts/
```

### Step 4: Install Dependencies

```python
!pip install torch transformers sentencepiece datasets evaluate sacrebleu \
            accelerate>=1.1.0 optimum[onnxruntime] onnx onnxruntime \
            pandas numpy
```

### Step 5: Verify GPU

```python
import torch
print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))
print("VRAM:", round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1), "GB")
```

### Step 6: Apply Bug Fixes (Required — See Section 10)

Fix the 3 known bugs in `train_model.py` and `evaluate_model.py` before proceeding.

### Step 7: Run Training

```python
# Stage 1: Validation run (500k subset, ~1–2 hours on A100)
!python scripts/train_model.py

# After confirming BLEU looks reasonable:
# Stage 2: Edit MAX_TRAIN_SAMPLES = None in train_model.py, then full run
!python scripts/train_model.py
```

### Step 8: Save Checkpoints to Drive Immediately

```python
import shutil
shutil.copytree(
    'models/marlish_mt5_finetuned/',
    '/content/drive/MyDrive/MarlishAI/checkpoints/'
)
```

> ⚠️ Do this after every session. Colab disconnections are not recoverable without saved checkpoints.

### Colab GPU Comparison

| GPU | VRAM | Stage 1 (500k) | Stage 2 (14.7M) | Notes |
|---|---|---|---|---|
| A100 | 40–80GB | ~45–60 min | ~8–12 hours | Best option; use if available |
| V100 | 16GB | ~90–120 min | ~18–24 hours | Good fallback |
| T4 | 16GB | ~2–3 hours | ~30–40 hours | Free tier; slow but works |
| Local RTX 3060 | 12GB | ~3–4 hours | ~40–60 hours | Use with BF16 on Windows |

---

## 8. Getting Started — Local RTX GPU

For contributors running on a local machine with an NVIDIA GPU.

### Prerequisites

- Python 3.10–3.13
- Node.js 18+
- NVIDIA GPU with ≥8GB VRAM (RTX 3060 12GB recommended minimum)
- CUDA 12.4 installed

### Step 1: Clone the Repository

```bash
git clone https://github.com/SanketShendge21/MarlishAI.git
cd MarlishAI
npm install
```

### Step 2: Build the Dictionary (Web App)

```bash
npm run build-dict
```

This compiles all source CSVs into `public/dictionary.json`. Required before running the web app.

### Step 3: Set Up Python Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 4: Install PyTorch with CUDA 12.4

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

Then install remaining dependencies:

```bash
pip install transformers sentencepiece datasets evaluate sacrebleu \
            accelerate>=1.1.0 optimum[onnxruntime] onnx onnxruntime \
            pandas numpy
```

### Step 5: Verify GPU

```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
```

### Step 6: Extract Training Data

```bash
unzip ml_splits.zip -d docs/Dictionary_Refs/ml_splits/
```

### Step 7: Apply Bug Fixes (Required — See Section 10)

### Step 8: Train & Export

```bash
# Stage 1: 500k validation run (~3–4 hours on RTX 3060)
python scripts/train_model.py

# After verifying BLEU: full training (~40–60 hours, resumable with Ctrl+C)
# Edit MAX_TRAIN_SAMPLES = None in train_model.py first
python scripts/train_model.py

# Export to ONNX + quantize
pip install optimum[onnxruntime] onnx onnxruntime
python scripts/export_onnx.py

# Evaluate
python scripts/evaluate_model.py
```

### Step 9: Start the Web App

```bash
npm run dev
```

---

## 9. Critical Technical Details

Read every item here before running any training script.

---

### ⚠️ BF16 — Not FP16

**The `mT5-small` model MUST be trained with `bf16=True`, not `fp16=True`.**

mT5 uses activations that overflow the FP16 range, causing loss to collapse to `0` or produce `NaN` within the first few hundred steps. BF16 has the same memory savings (2 bytes per parameter) but a much wider dynamic range, which mT5 requires.

```python
# CORRECT — use this in TrainingArguments
training_args = TrainingArguments(
    bf16=True,   # ✅ Correct for mT5
    fp16=False,  # ✅ Explicitly disable
    ...
)

# WRONG — causes NaN loss within the first epoch on mT5
training_args = TrainingArguments(
    fp16=True,   # ❌ Do NOT use this
    ...
)
```

BF16 requires Ampere (RTX 30xx) or newer GPUs. On Colab, A100 and V100 both support it.

---

### ⚠️ Directional Task Prefixes Are Mandatory

The model is multi-task. Without the prefix, it has no way to know which language to output.

```python
# CORRECT — always prefix before inference
input_text = "translate Hinglish to English: kal milte hai bro"

# WRONG — model behavior undefined without prefix
input_text = "kal milte hai bro"
```

Prefixes are automatically added by `train_model.py` from the `direction` column during training. For manual inference or testing, you must add them yourself.

---

### ⚠️ Memory Management (OOM Prevention)

Default batch size is `32` (safe for 12GB VRAM on RTX 3060). If you hit Out of Memory:

```python
# In train_model.py — reduce batch, maintain effective batch size with accumulation
per_device_train_batch_size = 16    # Halved
gradient_accumulation_steps = 2    # Doubles effective batch → still 32 effectively
```

For 8GB cards (RTX 3070 mobile, etc.), go to batch size 8 with accumulation 4.

---

### ⚠️ Checkpoint Resume — Always Use It

Training takes 40–60 hours. Never start from scratch if a checkpoint exists.

```python
# In TrainingArguments
output_dir = "models/marlish_mt5_finetuned/"
resume_from_checkpoint = True  # Auto-detects latest checkpoint in output_dir
```

Checkpoints are saved every 2,000 steps. A safe Ctrl+C during training will not corrupt the last saved checkpoint.

---

### ⚠️ ONNX Export Output File Names

After export, the browser expects these specific files in `public/models/`:

```
public/models/
├── encoder_model_quantized.onnx
├── decoder_model_quantized.onnx
├── decoder_with_past_model_quantized.onnx
└── tokenizer/
    ├── tokenizer.json
    ├── tokenizer_config.json
    └── spiece.model
```

If file names differ from what `Transformers.js` expects, the browser will silently fail to load the model. Check `lib/tier-router.js` for the exact paths it references.

---

### ⚠️ Normalization Must Run Before ML Inference

The ML model was trained on clean, normalized text. Do not pass raw abbreviations like `kr rha h` directly to the model — always run `typo-map.js` normalization first. In the browser pipeline, `tier-router.js` handles this automatically. For any offline testing scripts, apply normalization manually.

---

### ⚠️ Model Size Targets

| Stage | Format | Size | Usage |
|---|---|---|---|
| After training | PyTorch `.bin` / `.safetensors` | ~1.2GB | Training only — never deployed |
| After ONNX export | FP32 ONNX | ~300MB | Intermediate only |
| After INT8 quantization | ONNX INT8 | **< 40MB** | Production browser target |

Do not deploy the unquantized ONNX. The 40MB target is non-negotiable for mobile users.

---

## 10. Known Bugs to Fix Before Training

There are **3 confirmed bugs** in the provided scripts. Fix all three before running `train_model.py` or `evaluate_model.py`.

---

### Bug 1 — `train_model.py`: Stale docstring and sample prefix format

**Severity:** Low (cosmetic, but produces misleading output)

**Location:** Lines 1–6 (docstring) and line 272 (sample translations section)

**Problem:**
- Docstring still reads "CPU-Optimized / MarianMT" — should say "GPU-Optimized / mT5-small"
- Sample translation section uses the old `>>eng<<` prefix format instead of the current `translate X to Y:` multi-task format

**Fix:**
```python
# Line 1–6: Update banner comment
# ❌ Old: "CPU-Optimized MarianMT Training Script"
# ✅ New: "GPU-Optimized mT5-small Fine-Tuning Script"

# Line 272: Update sample translation prefix
# ❌ Old: tokenizer(">>eng<< " + sample_text, ...)
# ✅ New: tokenizer("translate Hinglish to English: " + sample_text, ...)
```

---

### Bug 2 — `train_model.py`: Balanced sampling divides by 4, not 8

**Severity:** Medium (doubles Stage 1 training time silently)

**Location:** Line 144

**Problem:**
```python
# ❌ Bug: hardcoded 4 directions
per_dir = MAX_TRAIN_SAMPLES // 4
# Result: samples 125k per direction → 1M total (2x intended for Stage 1)
```

**Fix:**
```python
# ✅ Fix: derive from actual direction count
per_dir = MAX_TRAIN_SAMPLES // train_df['direction'].nunique()
# Result: samples 62.5k per direction → 500k total (correct Stage 1 size)
```

---

### Bug 3 — `evaluate_model.py`: Hardcoded prefix map only covers 4 directions

**Severity:** Medium (breaks evaluation for all English→X reverse directions)

**Location:** Lines 26–32

**Problem:**
```python
# ❌ Bug: only covers 4 of 8 directions
prefix_map = {
    "hinglish_to_english": "translate Hinglish to English: ",
    "marlish_to_english":  "translate Marlish to English: ",
    "hindi_to_english":    "translate Hindi to English: ",
    "marathi_to_english":  "translate Marathi to English: ",
    # Missing all 4 English→X directions
}
```

**Fix:**
```python
# ✅ Fix: either add all 8, or derive dynamically
def get_prefix(direction: str) -> str:
    parts = direction.split("_to_")
    src = parts[0].replace("_", " ").title()
    tgt = parts[1].replace("_", " ").title()
    return f"translate {src} to {tgt}: "
```

---

## 11. Training Strategy & Checkpoint Log

Training uses a two-stage strategy to validate the pipeline before committing to the full multi-day run.

### Stage 1 — Pipeline Validation Run

**Purpose:** Confirm the entire pipeline works end-to-end before investing 40+ hours.

**Config:** `MAX_TRAIN_SAMPLES = 500_000` (62.5k × 8 directions)

**Estimated time:**
- RTX 3060 (local): ~3–4 hours
- V100 (Colab): ~1.5–2 hours
- A100 (Colab): ~45–60 minutes

**Criteria to pass Stage 1 and proceed to Stage 2:**
- Training loss decreases across first 2,000 steps
- BLEU score on validation set > 5 (even low BLEU is fine at this stage — you're checking the pipeline, not quality)
- ONNX export succeeds and loads in the browser without errors
- At least 3 sample translations look directionally correct (not garbage)

### Stage 2 — Full Production Training

**Config:** `MAX_TRAIN_SAMPLES = None` (all 14.7M training rows)

**Estimated time:**
- RTX 3060 (local): ~40–60 hours (resumable across sessions)
- V100 (Colab): ~18–24 hours
- A100 (Colab): ~8–12 hours

### Training Session Log

Update this table after every training session:

| Session # | Date | Contributor | Target | Start Checkpoint | End Checkpoint | Steps Completed | Train Loss | Val BLEU | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | TBD | — | 500k subset | Fresh (step 0) | `checkpoint-????` | — | — | — | Stage 1 validation |
| 2 | TBD | — | Full 14.7M | Resume from #1 | `checkpoint-????` | — | — | — | Full production run |

### Training Configuration Reference

| Parameter | Value | Reason |
|---|---|---|
| Base model | `google/mt5-small` | Best multilingual Seq2Seq for browser deployment |
| Parameters | ~300M | Largest feasible for INT8 < 40MB browser target |
| Batch size | 16–32 | 16 safe for 12GB VRAM; 32 for 16GB+ |
| Epochs | 3 | Standard for Seq2Seq fine-tuning |
| Learning rate | 3e-5 | Standard mT5 fine-tuning LR |
| Warmup steps | 500 | Gradual ramp prevents early instability |
| Eval steps | 1,000 | BLEU check every 1k steps |
| Save steps | 2,000 | Resumable checkpoint cadence |
| Max sequence length | 128 tokens | Covers ~99% of sentences in dataset |
| Precision | BF16 | Required for mT5 (see Section 9) |

---

## 12. ONNX Export & Browser Deployment

After training completes, the PyTorch model must be converted for browser use.

### Export Command

```bash
pip install optimum[onnxruntime] onnx onnxruntime
python scripts/export_onnx.py
```

### What the Script Does

1. Loads the best checkpoint from `models/marlish_mt5_finetuned/final/`
2. Traces the encoder and decoder computational graphs
3. Exports to ONNX FP32 (~300MB)
4. Applies INT8 dynamic quantization → target **< 40MB**
5. Saves quantized files to `models/onnx/`

### Deploying to the Browser

```bash
# Copy ONNX files to the public directory for Next.js to serve
cp -r models/onnx/ public/models/
```

The browser loads the model via `lib/tier-router.js` using `Transformers.js`:
- Model is loaded **lazily** — only on the first Tier 2 invocation (confidence < 0.7)
- Model weights are cached in **IndexedDB** after the first load → fully offline after that
- Inference runs in a **Web Worker** → main UI thread is never blocked

### Browser Performance Targets

| Metric | Target | Notes |
|---|---|---|
| First-load model download | < 40MB | After INT8 quantization |
| Model cache load (IndexedDB) | < 1 second | After first download |
| Tier 2 inference latency | < 500ms | Via WASM ONNX Runtime |
| Browser memory footprint | < 100MB | Model + runtime + dictionary |

---

## 13. Development Tips & Workflow

### Testing the NLP Engine

Before committing any changes to `lib/`, always run the test suite:

```bash
node tests/test-engine.js
```

Tests cover: exact phrase matches, ambiguous word resolution, SOV→SVO reordering, typo normalization, and confidence scoring. A passing test suite before and after your change means you haven't broken existing behavior.

### Rebuilding the Dictionary

When you add new words or phrases to the source CSV files, recompile to `dictionary.json`:

```bash
npm run build-dict
```

Changes to source CSVs are **not** reflected in the running app until you rebuild.

### Running the Web App

```bash
npm run dev   # Development server (hot reload)
npm run build # Production build
npm start     # Start production server
```

### Adding New Normalization Rules

Edit `lib/typo-map.js`. Format:

```js
const typoMap = {
  // abbreviation: canonical_form
  "kr":  "kar",
  "rha": "raha",
  "h":   "hai",
  "nhi": "nahi",
  // add new entries here
};
```

After adding entries, run `node tests/test-engine.js` to confirm no regressions.

### Adding New Grammar Templates

Edit `lib/grammar-rules.js`. Templates are ordered — more specific patterns should appear before more general ones.

```js
const grammarRules = [
  {
    // Pattern: SOV with auxiliary
    pattern: /^(.+)\s+(ja raha hu|ja rahi hu)$/,
    replace: "I am going $1"
  },
  // Add new templates here — more specific first
];
```

### Confidence Score Calibration

If you add a new layer or a new match type, add a corresponding constant to `lib/scoring-engine.js`:

```js
export const SCORE_WEIGHTS = {
  EXACT_PHRASE:     1.00,
  DIRECT_DICT:      0.90,
  CONTEXTUAL:       0.80,
  FUZZY:            0.65,
  GRAMMAR_REPAIR:  -0.05,  // penalty per repair applied
  UNKNOWN_TOKEN:   -0.20,  // penalty per passthrough token
  // YOUR_NEW_LAYER: X.XX
};
```

Getting this wrong will mis-fire the ML fallback threshold and degrade Tier 1 accuracy metrics.

---

## 14. Contribution Checklist

Use this before submitting any contribution.

### Before Starting

- [ ] Read this entire document
- [ ] Fix all 3 bugs in `train_model.py` and `evaluate_model.py` (Section 10) before any training run
- [ ] Verify GPU is detected: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Confirm `DATA_DIR` in `train_model.py` matches your local extraction path for `ml_splits.zip`

### For NLP Engine Changes (`lib/`)

- [ ] `node tests/test-engine.js` passes before your change
- [ ] `node tests/test-engine.js` passes after your change
- [ ] New score constants added to `scoring-engine.js` if you added a layer
- [ ] `npm run build-dict` run if you changed any source CSV

### For ML Pipeline Changes (`scripts/`)

- [ ] Bug fixes from Section 10 are applied
- [ ] Stage 1 (500k) run completes without NaN loss
- [ ] BLEU > 5 on validation set after Stage 1
- [ ] ONNX export produces files < 40MB
- [ ] Browser loads the model without console errors
- [ ] Training session log (Section 11) updated with your session details
- [ ] Final model checkpoint saved to cloud storage (Drive / S3) — **not just local disk**

### General

- [ ] No raw `pytorch_model.bin` committed to git (too large — use `.gitignore`)
- [ ] `docs/progress_tracker.md` updated with status changes
- [ ] No hardcoded file paths — use relative paths from project root

---

## 15. Requirements Reference

### `requirements.txt`

```text
# Core ML
torch
transformers>=4.40.0
sentencepiece
datasets
evaluate
sacrebleu
accelerate>=1.1.0

# ONNX Export & Quantization
optimum[onnxruntime]
onnx
onnxruntime

# Data Processing
pandas
numpy

# Optional: Jupyter (for Colab notebook)
jupyterlab
ipywidgets
```

### `package.json` Key Scripts

| Script | Command | Purpose |
|---|---|---|
| `dev` | `next dev --turbo` | Development server with hot reload |
| `build` | `next build` | Production build |
| `build-dict` | `node scripts/build-dictionary.js` | Recompile `dictionary.json` from source CSVs |
| `test` | `node tests/test-engine.js` | Run NLP engine test suite |

### Environment Variables (`.env.local`)

```env
# Optional — for analytics or feedback collection
NEXT_PUBLIC_APP_VERSION=1.0.0

# ML model path (relative to /public)
NEXT_PUBLIC_MODEL_PATH=/models
```

---

*Let's build the future of Indian chat together.* 🚀

---

> **Questions?** Open an issue on [GitHub](https://github.com/SanketShendge21/MarlishAI) or check `docs/progress_tracker.md` for the current task state.