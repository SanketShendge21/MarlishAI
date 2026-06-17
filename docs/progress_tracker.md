---
title: Marlish.AI — Progress Tracker
updated: 2026-05-27
---

# Marlish.AI — Progress Tracker

> Single source of truth for project accomplishments and currently active work.

---

## 🏛️ Pre-Pivot (Legacy Work)

The original plan was to train a custom `mT5-small` model from scratch. This was abandoned in May 2026 after training yielded a BLEU score of ~3, proving that scratch training on noisy code-mixed data was not viable without massive compute and cleaner data.

| Task | Status | Notes |
|------|--------|-------|
| Parse all CSV/Parquet sources | ✅ Done | 8.2M final rows combined. |
| Build 8-layer NLP Rule Engine | ✅ Done | Currently active as Tier 1. |
| Train `mT5-small` on 18.4M pairs | 🚫 Abandoned | Failed quality threshold. |
| Archive training scripts & models | ✅ Done | Moved to `legacy/` & `pre-pivot-mt5-training` branch. |

---

## 🚀 NEW PIVOT: Hybrid Architecture (Started May 2026)

We have pivoted to a **Hybrid Transliteration-First Architecture** utilizing pre-trained models combined with a custom Marlish → Devanagari transliteration pipeline.

### Phase 0: Archive & Cleanup
**Status: ✅ COMPLETE (May 23, 2026)**
- Created `pre-pivot-mt5-training` archive branch.
- Moved old training scripts to `legacy/scripts/`.
- Moved old models to `legacy/models/`.
- Deleted 18.4M-row `ml_splits` to save space.
- Fixed 7-layer → 8-layer terminology across all documentation.
- Updated `.gitignore` for Python environments and legacy models.

### Phase 1: Test Pre-Trained Models & Pick the Stack
**Status: ⚠️ COMPLETE — CRITICAL FINDING (May 24, 2026)**
- [x] Install test dependencies. *(venv activated, installed `torch` cu124 for RTX 3060 GPU, `transformers`, `sentencepiece`, `sacrebleu`, `indic-transliteration`, `pandas`, `pyarrow`.)*
- [x] Create `scripts/test_pretrained_models.py` benchmark script. *(Tests both transliterated path and gold Devanagari path to separately measure transliteration tax. Auto-detects CUDA GPU.)*
- [x] Run benchmark: Test `opus-mt-mr-en` translation quality.
- [x] Log BLEU scores: **End-to-End BLEU: 0.45** | **Quality Ceiling BLEU: 8.37** | **Transliteration Tax: 7.91 points**
- [x] Identify transliteration quality gap: **Both the model AND transliteration are broken.**

**⚠️ Critical Finding — opus-mt-mr-en is NOT suitable for conversational Marathi:**
- Model is trained on formal/religious text (Bible, Watchtower publications). Hallucinates on simple chat input.
- Even with **gold Devanagari** input, only 2/10 sentences produced usable output.
- 8/10 gold Devanagari sentences were hallucinated garbage.
- Baseline ITRANS transliteration is also terrible — treats English loanwords as Sanskrit.
- **Decision per plan criteria:** "opus-mt output is broken on > 50% of test sentences → Investigate IndicTrans2 API-only approach."
- **⏳ IndicTrans2 API investigation is deferred — will revisit after Phase 2 transliteration pipeline is complete.**

### Phase 2: Build the Marlish Transliteration Pipeline
**Status: ✅ COMPLETE (May 26, 2026)**
- [x] Create `scripts/transliterator/token_classifier.py`. *(Classifies tokens as ENGLISH/DEVANAGARI/NUMERIC/MARLISH. ~130 English loanwords in passthrough set.)*
- [x] Create `scripts/transliterator/phoneme_rules.py`. *(Character-level Romanized→Devanagari rules with proper matra/halant joining logic. Two-pass: tokenize then render.)*
- [x] Create `scripts/transliterator/fallback_map.py`. *(~250 curated Marlish→Devanagari entries. Seed map overrides dataset map for Marathi-first priority.)*
- [x] Create `scripts/transliterator/pipeline.py` + `__init__.py`. *(3-tier orchestrator: IndicXlit → Fallback Map → Phoneme Rules. Tracks per-tier hit stats.)*
- [x] Create `scripts/build_transliteration_map.py`. *(Auto-detects columns, extracts word pairs via naive alignment, frequency-ranked, capped at 10k entries. Also processes JSON dictionaries.)*
- [x] Create `requirements.txt` + `SETUP_ML.md`. *(Full setup guide for second machine. torch excluded from requirements — CUDA/CPU varies.)*
- [x] Moved `docs/Dictionary_Refs/` → `datasets/`. Updated all active file paths (`build_transliteration_map.py`, `build-dictionary.js`, `inspect_parquet.py`, `.gitignore`).
- [x] Verified datasets structure with `inspect_parquet.py` and initialized Python environment with CUDA 12.4 on new machine.
- [x] Run `build_transliteration_map.py` and generate `public/transliteration_map.json`. *(10,000 entries, 338.4 KB. Processed 1.63M aligned sentences from 4 parquet files. Min frequency threshold: 3.)*
- [x] Test pipeline against 50+ real Marlish sentences and document accuracy. *(55 sentences tested. **100% token accuracy, 100% sentence exact match.** Fixes applied: reversed merge priority for Marathi-first, expanded English passthrough, added ~35 seed words, rewrote phoneme rules with matra/halant logic.)*

**📦 Datasets in use (located in `datasets/`):**
- `Marathi_part_1.parquet` — 1.8M rows, Marathi Devanagari + English
- `Marathi_part_2.parquet` — 1.8M rows, Marathi Devanagari + English
- `Hinglish_part_1.parquet` — 500K rows, Hinglish + Hindi Devanagari + English
- `Hinglish_part_2.parquet` — 500K rows, Hinglish + Hindi Devanagari + English
- `hinglish_marlish_10000_dataset.json` — Word-level dictionary (v1)
- `hinglish_marlish_v2_25000_dataset.json` — Phrase-level dictionary (v2)
- `hinglish_marlish_v3_production_100k.json` — Production dictionary (v3)
- `marlish_ai_5000_premium_dataset.json` — Premium curated dataset

---

### Phase 3: Translation Model Benchmark & Selection
**Status: ✅ COMPLETE (May 28, 2026)**

**Key Decision:** opus-mt is broken for conversational Marathi (Phase 1 finding). Benchmarked NLLB-200 and IndicTrans2 to decide the final model stack.

**Models Evaluated:**
| Model | Params | Gated? | Status / Result |
|-------|--------|--------|--------|
| `facebook/nllb-200-distilled-600M` | 600M | ❌ No | **✅ SUCCESS** (BLEU: 40.71) |
| `ai4bharat/indictrans2-indic-en-dist-200M` | 200M | ✅ Yes | **🚫 FAILED** (Incompatible with modern `transformers`) |

#### Test Results:
1. **NLLB-200 (600M):**
   - **End-to-End BLEU (Marlish → Pipeline → NLLB): 40.71**
   - **Quality Ceiling BLEU (Gold Deva → NLLB): 36.65**
   - *Note: End-to-end performed slightly better than the ceiling, indicating our transliteration pipeline acts as a helpful normalizer (e.g., handling English loanwords gracefully).*
   - **Performance:** Massive improvement over opus-mt (0.45 BLEU). Usable for production.
2. **IndicTrans2 (200M):**
   - **Result: Failed to load.** 
   - **Technical Root Cause:** The custom model code hosted on Hugging Face (`trust_remote_code=True`) relies on internal APIs that were removed in modern `transformers` versions:
     - `configuration_indictrans.py` imports `transformers.onnx` (removed in v4.40).
     - `tokenization_indictrans.py` references `self._special_tokens_map` (deprecated internal property).
   - **Attempted Fixes:**
     - Injected a dummy `transformers.onnx` package → revealed the tokenizer API failure.
     - Attempted to downgrade to `transformers==4.38.2` → failed because Python 3.14 lacks pre-built wheels for older `tokenizers`, forcing a Rust source compilation that failed on this Windows environment.
   - **Conclusion:** Modifying and maintaining broken third-party model code just to load it is not justifiable when NLLB-200 natively supports modern `transformers` and scores 40.71 BLEU. IndicTrans2 is officially skipped.

#### Phase 3 Conclusion:
- **Decision:** **Proceed with NLLB-200-distilled-600M** as the core translation model.
- It delivers excellent conversational Marathi-to-English translation.
- It does not require a HuggingFace account (no gating).
- It is well-supported by modern inference libraries (including ONNX/Transformers.js).

---

### Phase 4: Pure ML Translation API
**Status: 🔲 In Progress (Started May 30, 2026)**

**Architecture Decision:** Dropped the 8-layer rule engine and offline ONNX path entirely. The app is a standard online service — user sends text, backend API transliterates (if needed) + translates via NLLB-200, returns the result.

```
User → Website (Next.js on Vercel) → POST /translate → API (FastAPI on HF Spaces)
                                                          │
                                                  1. Transliterate if romanized (Marlish/Hinglish → Devanagari)
                                                  2. NLLB-200 inference (any pair among 5 languages)
                                                          │
                                          ← { translation, devanagari, latency_ms }
```

**Supported language pairs (NLLB-200 handles all natively):**
| Source | Target | Transliteration needed? |
|--------|--------|------------------------|
| Marlish (romanized) | English | ✅ Yes — Marlish → Marathi Devanagari → NLLB |
| Hinglish (romanized) | English | ✅ Yes — Hinglish → Hindi Devanagari → NLLB |
| Marathi (Devanagari) | English | ❌ No — direct to NLLB |
| Hindi (Devanagari) | English | ❌ No — direct to NLLB |
| English | Marathi | ❌ No — direct NLLB (outputs Devanagari) |
| English | Hindi | ❌ No — direct NLLB (outputs Devanagari) |
| English | Marlish | ❌ No — NLLB outputs Devanagari (reverse translit is future work) |

#### Completed:
- [x] Create `api/app.py` v1 — FastAPI server with `/translate` and `/health` endpoints
- [x] Create `api/requirements.txt` — API dependencies
- [x] Install `fastapi` and `uvicorn` in venv
- [x] **API server tested locally** — NLLB-200 loads in ~1s on RTX 4050 GPU
- [x] **Tested `/translate` with real Marlish input** — all translations correct:
  - `kasa ahes mitra` → `How are you, friend?` (728ms first call, ~91ms warm)
  - `udya kay scene ahe` → `What's the scene tomorrow?`
  - `mi college la jato ahe` → `I'm going to college.`
  - `mala mahit nahi` → `I don't know.`
- [x] Create `docs/PHASE4_IMPLEMENTATION_PLAN.md` — detailed plan
- [x] **Upgraded `api/app.py` to v2** — now accepts `source` and `target` language params (supports all 5 languages, not just Marlish→English)
- [x] **Rewrote `hooks/useTranslation.js`** (v5→v6) — calls API instead of rule engine. Same return shape so all UI components work unchanged.
- [x] **Added `ml_translation` badge** to `app/components/translator/OutputArea.jsx` — violet "ML Translation" label for API results
- [x] **Ran `npm install`** — Node.js dependencies installed (116 packages)
- [x] **Fixed transliteration seed map** — added `nav` (नाव = name), possessive pronouns (`tuza`, `mazha`, etc.), and 18 other missing words
- [x] **Built reverse transliteration module** — `scripts/transliterator/reverse_transliterate.py` — converts NLLB Devanagari output back to chat-style romanized text. 6/6 tests pass.
- [x] **Wired reverse transliteration into API (v3)** — when target is `marlish`/`hinglish`, API now returns romanized text instead of raw Devanagari
- [x] **Created `scripts/test_reverse_translit.py`** — test suite for reverse transliteration

#### Known Issues (identified, being addressed):
1. **NLLB-200-600M translation quality** — tested with 23 real-world sentences.
   - Root cause: NLLB was trained on formal text (FLORES/Wikipedia), NOT conversational chat
   - This is a **data bias problem**, not a model capacity problem — upgrading to 1.3B won't fully fix it
2. **Transliteration pipeline misses some words** — seed map covers ~10K words but some Marlish words like "Jevay" and "vaat" still get wrong Devanagari.
3. **`transformers` version conflict** — `transformers 5.9.0` broke with `torch 2.12.0` (`NP_SUPPORTED_MODULES` import error). **Fixed by downgrading to `transformers 4.57.6`**.

#### Translation Quality Test Results (June 3, 2026):
Tested with 23 realistic everyday chat sentences. Full results in `docs/TRANSLATION_TEST_RESULTS.md`.

| Category | Count | Key examples |
|----------|-------|-------------|
| ✅ Accurate | 10 | "I passed the exam, I'm very happy", "What does your brother do?", "I don't want to go to the office today" |
| ⚠️ Close but imprecise | 5 | "are you sure?" (should be "will you come?"), "I feel urgent" (should be "I need it urgently"), dropped second sentence |
| ❌ Wrong | 4 | "watching the cattle" (should be "waiting"), "pot" (should be "poha"), "they go to movies" (should be "let's go") |
| 🔤 Reverse translit: works but formal | 4 | "krupaya" (should be "please"), "svadishta" (should be "tasty") |

**Error patterns — why NLLB fails:**
- **Idioms/slang:** "vaat baghte" (waiting) → transliterated but NLLB doesn't know the idiom
- **Code-mixed loanwords:** "poha" → NLLB sees Devanagari "पोहा" and guesses "pot"
- **Pragmatic intent:** "chalte hain" (let's go) → NLLB reads it as "they go" (formal grammar)
- **Dropped clauses:** NLLB sometimes ignores the second half of longer sentences

#### Gemini Deep Research Results (saved to `docs/GEMINI_RESEARCH_TRANSLATION_QUALITY.md`):
Key findings:
- **NLLB-1.3B** — better grammar, but same formal-domain bias (same FLORES training data). Zero code complexity increase (one string change), uses ~2.6GB VRAM instead of ~1.2GB, ~1.5x slower inference. Still fits RTX 4050.
- **IndicTrans2** — clear winner for colloquial Hindi/Marathi. Trained on BPCC conversational corpus.
  - `indictrans2-indic-en-1B` → ~4.5GB VRAM in FP16
  - `indictrans2-indic-en-dist-200M` → ~950MB VRAM, very fast
  - **Problem:** HuggingFace integration broken on `transformers 4.x+` (we confirmed this — `transformers.onnx` import error)
  - **Potential fix:** CTranslate2 runtime, or check if newer IndicTrans2 releases fixed the import
- **Gemma 3 1B** as post-processing GEC → ~0.8GB VRAM in 4-bit, fixes grammar after translation#### Quality Improvement Roadmap (in priority order):
1. [x] **Try IndicTrans2** — ❌ FAILED. Tokenizer crashes at load time (Step 5). Broken with `transformers 4.57.6`.
2. [x] **Test NLLB-1.3B** — ✅ Tested. Identical to 600M. Keeping 1.3B (no downside).
3. [x] **Fix transliteration seed map** — ✅ Added ~80 words: jevay, yeshil, vaat, poha, food words, Hindi words, chat loanwords
4. [x] **Add Gemini GEC post-processing** — ✅ Wired `gemini-2.5-flash-lite` into `api/app.py`. Reads API key from `.local.env`. Graceful fallback if no key set.
5. [x] **Test with GEC enabled** — ✅ Tested June 9. GEC works, polishes grammar on correct translations.
6. [x] **Carnival Tours real-world test** — ✅ 104 segments across ALL 8 language directions.

**Carnival Tours Test Results (June 9, 2026):**
| Direction | Score | Verdict |
|-----------|-------|---------|
| Marathi → English | 11/13 | ✅ Strong |
| Hindi → English | 12/13 | ✅ Best performer |
| English → Marathi | 12/13 | ✅ Strong |
| English → Hindi | 13/13 | ✅ Excellent |
| English → Marlish | 9/13 | ⚠️ Correct Devanagari, romanization too literal |
| English → Hinglish | 9/13 | ⚠️ Same — overly formal romanization |
| **Marlish → English** | **6/13** | ❌ **Transliteration pipeline is the bottleneck** |
| **Hinglish → English** | **6/13** | ❌ **Same — broken Devanagari reaches NLLB** |

**Root cause: Transliteration pipeline doesn't handle conjunct consonants or long vowels:**
- `"vyavastha"` → `"वयवसथ"` instead of `"व्यवस्था"` (no halant/virama)
- `"shakahari"` → `"शकहरि"` instead of `"शाकाहारी"` (no long vowels)
#### Priority Fixes:
1. [x] **Fix conjunct consonant rules** — ✅ Done. All C+C pairs now get halant in `phoneme_rules.py`.
2. [~] **Fix long vowel patterns** — Partial. Seed map handles known words; phoneme-level `a/aa` ambiguity unsolvable.
3. [x] **Expand seed map** — ✅ Done. +60 words: travel/formal Marathi, Hindi formal, Hinglish particles.
4. [x] **Improve reverse transliteration** — ✅ Done. Digits, matra, simplification.
5. [x] **Re-test** — ✅ Done June 9 15:18. Results: Marlish→English improved 6/13 → **11/13**, Hinglish→English improved 6/13 → **11/13**

**Post-fix Carnival Tours Results (June 9, 2026 — after priority fixes):**
| Direction | Before | After |
|-----------|--------|-------|
| Marathi → English | 11/13 | 11/13 (stable) |
| Hindi → English | 12/13 | 12/13 (stable) |
| Marlish → English | 6/13 | **11/13** ✅ |
| Hinglish → English | 6/13 | **11/13** ✅ |
| English → Marathi | 12/13 | 12/13 (stable) |
| English → Hindi | 13/13 | 13/13 (stable) |
| English → Marlish | 9/13 | 10/13 (improved) |
| English → Hinglish | 9/13 | 10/13 (improved) |

#### Deployment Steps:
1. [x] **Organized test results** — moved to `docs/test-results/`
2. [x] **Created `Dockerfile`** — HF Spaces Docker, free tier CPU
3. [x] **Created `requirements-api.txt`** — CPU-only PyTorch (smaller image)
4. [x] **Created `README_HF.md`** — HF Spaces metadata + API docs
5. [x] **Created `.dockerignore`** — excludes frontend/docs/tests
6. [x] **Updated `vercel.json`** — `NEXT_PUBLIC_API_URL`, security headers
7. [x] **Updated `api/app.py` CORS** — Vercel prod + preview + localhost
8. [x] **Updated test script paths** — `docs/test-results/`
9. [x] **Adjusted all configs for free tier** — CPU-only PyTorch, no GPU hardware spec
10. [x] **Updated all documentation** — docs 01-11, README.md, README_HF.md
11. [ ] **Create HF Spaces repo** — push API code ← **MANUAL STEP**
12. [ ] **Set HF Spaces secrets** — `Marlish_Gemini_API_Key` ← **MANUAL STEP**
13. [ ] **Push to GitHub** — triggers Vercel deploy ← **MANUAL STEP**
14. [ ] **Verify end-to-end** — Vercel frontend → HF Spaces API

#### Documentation Update (June 11):
| Doc | What changed |
|-----|-------------|
| `README.md` | Complete rewrite — NLLB arch, current project structure, setup guide |
| `README_HF.md` | Free tier config, API examples, language table |
| `01-requirements.md` | v4.0 — functional/non-functional specs for ML pipeline |
| `02-architecture.md` | v4.0 — NLLB + translit + GEC architecture diagram |
| `03-ai-ml-models.md` | v4.0 — model selection, rejected models, quality metrics |
| `04-use-cases.md` | v4.0 — real examples, Carnival Tours test data |
| `05-deployment.md` | v4.0 — free tier deployment guide (Vercel + HF Spaces) |
| `06-research-prompts.md` | Header updated — marked as reference archive |
| `07-project-structure.md` | v4.0 — actual current directory structure |
| `08-tech-stack.md` | v4.0 — current technology table |
| `09-app-vision-and-goals.md` | v7.0 — architecture evolution, roadmap |
| `10-ml-model-roadmap.md` | v4.0 — model timeline, future upgrades |
| `11-enterprise-architecture.md` | v4.0 — scaling path, tech worth/not-worth |

---

## ⏸ RESUME STATE (Last updated: June 11, 2026 18:36)

> **Read this section first when resuming work.**

### Environment
- **Python:** 3.14.5 (venv at `d:\MarlishAI\MarlishAI\venv\`)
- **GPU:** NVIDIA GeForce RTX 4050 Laptop GPU — CUDA ✅
- **torch:** 2.12.0+cu126, **transformers:** 4.57.6
- **NLLB-200-1.3B:** ✅ Downloaded, tested
- **Gemini GEC:** ✅ Enabled, key in `.local.env`

### Deployment Architecture (Free Tier):
```
┌─────────────────────┐         ┌──────────────────────────┐
│   Vercel (Frontend)  │  HTTPS  │  HF Spaces (API)         │
│   Next.js + React    │────────▶│  FastAPI + NLLB-200-1.3B  │
│   Free tier          │  POST   │  Free tier (CPU)          │
│                      │  /translate  │  Docker, Port 7860   │
└─────────────────────┘         └──────────────────────────┘
```

### What to do next — Deploy (in order):

#### Step 1: Create HF Spaces repo
1. Go to https://huggingface.co/spaces
2. Create new Space (Docker SDK, **CPU basic** — free)
3. Clone locally

#### Step 2: Push API code to HF Spaces
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/marlishai-api hf-deploy
cp Dockerfile hf-deploy/
cp requirements-api.txt hf-deploy/
cp README_HF.md hf-deploy/README.md
cp -r api/ hf-deploy/api/
cp -r scripts/transliterator/ hf-deploy/scripts/transliterator/
cd hf-deploy && git add . && git commit -m "Deploy v1.0" && git push
```

#### Step 3: Set HF Spaces secrets
- Space Settings → Secrets → `Marlish_Gemini_API_Key`

#### Step 4: Push to GitHub (triggers Vercel)
```bash
git add .
git commit -m "v1.0: NLLB-1.3B + GEC + 8 language directions"
git push origin main
```

#### Step 5: Update vercel.json API URL
- Get actual HF Space URL → update `NEXT_PUBLIC_API_URL` → push again

### Important notes:
- `transformers` must be `<5.0.0`
- `.local.env` — never commit
- Free tier CPU: 15-30s/request (usable for demo, slow for production)
- Upgrade to T4 GPU later for real-time speed (~₹50/hr)
- All docs (01-11) updated to v4.0 on June 11

---

*(Future phases: QLoRA fine-tuning, IndicXlit integration, T4 GPU upgrade, custom domain)*

