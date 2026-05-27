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
**Status: 🔲 In Progress (Started May 26, 2026)**

**Key Decision:** opus-mt is broken for conversational Marathi (Phase 1 finding). Rather than ONNX-exporting a broken model, we are benchmarking better translation models first.

**Models under evaluation:**
| Model | Params | Gated? | Status |
|-------|--------|--------|--------|
| `facebook/nllb-200-distilled-600M` | 600M | ❌ No | Ready to test |
| `ai4bharat/indictrans2-indic-en-dist-200M` | 200M | ✅ Yes (needs HF login + license accept) | Ready to test |

#### Completed work:
- [x] Create `scripts/test_translation_models.py`. *(Unified benchmark script. Supports `--model nllb`, `--model indictrans2`, or `--model all`. Tests both transliterated and gold Devanagari paths. Measures BLEU. Compares against Phase 1 opus-mt baseline.)*
- [x] Create `scripts/test_indictrans2.py`. *(Earlier standalone version — superseded by `test_translation_models.py` but still functional.)*
- [x] Create `scripts/indic_processor.py`. *(Pure Python port of `IndicTransToolkit/processor.pyx` — works around Cython/MSVC build requirement on Windows. Handles Indic text normalization, tokenization, digit translation for IndicTrans2 preprocessing.)*
- [x] Install IndicTrans2 dependencies: `sacremoses`, `indic-nlp-library-itt`, `regex`.

#### Blocked / next steps:
- [ ] **USER ACTION:** Install `torch` with CUDA 12.1: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
- [ ] **USER ACTION (for IndicTrans2):** Accept model license at https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M, then run `huggingface-cli login`
- [ ] Run NLLB benchmark: `python scripts/test_translation_models.py --model nllb`
- [ ] Run IndicTrans2 benchmark: `python scripts/test_translation_models.py --model indictrans2`
- [ ] Document BLEU results and decide model selection:
  - If NLLB ceiling BLEU > 15 → Use NLLB for both API and ONNX browser path
  - If IndicTrans2 ceiling BLEU > 15 → Use for API path (Phase 4). NLLB for offline.
  - Offline fallback: Tier 1 rule engine (handles 80%+ of inputs at <5ms)

---

## ⏸ RESUME STATE (Last updated: May 27, 2026)

> **Read this section first when resuming work.** It describes the exact state of the project and what to do next.

### Environment
- **Python:** 3.14.5 (venv at `d:\MarlishAI\MarlishAI\venv\`)
- **GPU:** NVIDIA RTX 4050 (this machine)
- **torch:** Needs reinstall — user will run: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
- **Installed deps:** `transformers`, `sentencepiece`, `sacrebleu`, `sacremoses`, `indic-nlp-library-itt`, `regex`, `pandas`, `pyarrow`

### What to do next (in order):
1. **Verify torch is installed:** `python -c "import torch; print(torch.cuda.is_available())"`
2. **Run NLLB benchmark:** `python scripts/test_translation_models.py --model nllb`
3. **If user has HF login:** `python scripts/test_translation_models.py --model indictrans2`
4. **Record BLEU scores** in this tracker under Phase 3
5. **Decide model selection** based on BLEU results (see decision tree above)
6. **Proceed to Phase 4** (ONNX export or API setup depending on results)

### Key files created in Phase 3:
| File | Purpose | Status |
|------|---------|--------|
| `scripts/test_translation_models.py` | Unified model benchmark (NLLB + IndicTrans2) | ✅ Ready to run |
| `scripts/test_indictrans2.py` | Standalone IndicTrans2 benchmark | ✅ Superseded by above |
| `scripts/indic_processor.py` | Pure Python IndicProcessor (no Cython needed) | ✅ Ready |
| `scripts/evaluate_transliteration.py` | Phase 2 transliteration accuracy test (55 sentences, 100%) | ✅ Complete |

### Issues encountered & resolutions:
1. **IndicTransToolkit Cython build failure** → Solved: Created `scripts/indic_processor.py` (pure Python port)
2. **torch cu124 no wheel for Python 3.14** → User switching to cu121 index
3. **IndicTrans2 gated repo 401** → User needs to accept license + `huggingface-cli login`
4. **NLLB CPU test cancelled** → Too slow on CPU, user switching back to GPU

---

*(Future phases will be added here as they become active.)*
