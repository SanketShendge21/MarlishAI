---
title: Marlish.AI — Progress Tracker
updated: 2026-05-23
---

# Marlish.AI — Progress Tracker

> Single source of truth for what has been done, what is in progress, and what is pending.
> Updated for the **IndicXlit + opus-mt Strategic Pivot** (May 2026).

---

## ⚠️ STRATEGIC PIVOT (May 2026)

The `mT5-small` scratch training attempt yielded BLEU ~3 — unusable for demo. After diagnosis, the project pivoted to a **Hybrid Transliteration-First Architecture**:

- **Transliteration:** AI4Bharat IndicXlit (primary) + frequency-ranked map from 3.6M parquet rows (offline fallback) + phoneme rules (last resort)
- **Translation:** Helsinki-NLP `opus-mt-mr-en` running in-browser via ONNX + Transformers.js
- **Architecture:** opus-mt in browser is v1. IndicTrans2 hosted API is explicitly scoped as v2 — it does not block shipping.

**Full analysis:** `docs/ARCHITECTURE_ANALYSIS_AND_PLAN.md`

---

## System & Environment Details

| Item | Value |
|------|-------|
| **Core NLP Engine** | 8-Layer JavaScript Rule Engine (Tier 1, < 5ms) |
| **Transliteration** | IndicXlit (Python, primary) + freq-map + phoneme rules |
| **Browser ML (v1)** | `Helsinki-NLP/opus-mt-mr-en` (ONNX INT8, < 75MB, offline) |
| **API ML (v2, optional)** | IndicTrans2 (hosted, not in v1 scope) |
| **Legacy Model (Archived)** | `google/mt5-small` (BLEU ~3, archived in `legacy/` and `pre-pivot-mt5-training` branch) |
| **Working Branch** | `Dev-Branch` |

---

## Pre-Pivot Work (Historical Record)

### Data Preparation — ✅ Complete

| Task | Status | Notes |
|------|--------|-------|
| Parse all source CSVs and Parquets | ✅ Done | 8+ million rows across all sources |
| Merge into `Combined_Parallel_Dataset.csv` | ✅ Done | 8,264,720 final rows after dedup |
| Remove duplicates & normalize text | ✅ Done | |
| Build `dictionary.json` (1.2MB) | ✅ Done | O(1) hash lookup, covers thousands of phrases |
| Build 8-Layer Rule Engine (`lib/dictionary-engine.js`) | ✅ Done | Handles ~80% of common inputs |
| Build PWA with Service Worker + IndexedDB | ✅ Done | Offline-first architecture |

### mT5-small Training — 🚫 Abandoned & Archived

| Task | Status | Notes |
|------|--------|-------|
| Fine-tune mT5-small on 18.4M pairs | 🚫 Abandoned | BLEU ~3, not recoverable |
| Evaluate model quality | ✅ Done | Diagnosis informed pivot decision |
| Archive scripts and checkpoints | 🔲 Pending | Move to `legacy/` folder + `pre-pivot-mt5-training` branch |

---

## Pivot Implementation Phases (New)

### Phase 0: Archive, Cleanup & Documentation Fix (~3 hours)

| Task | Status | Notes |
|------|--------|-------|
| Create `pre-pivot-mt5-training` git branch (archive) | 🔲 Pending | Preserve full training history |
| Move training scripts to `legacy/scripts/` | 🔲 Pending | `train_model.py`, `data_preprocessing.py`, `combine_datasets.py`, `evaluate_model.py`, `dataset_generator.py`, `marlish_colab_training.ipynb` |
| Move model checkpoints to `legacy/models/` | 🔲 Pending | `marlish_mt5_finetuned/`, `marlish_marianmt_finetuned/` |
| Delete `docs/Dictionary_Refs/ml_splits/` | 🔲 Pending | Large, regenerable, no longer needed |
| Add legacy note to `README.md` | 🔲 Pending | |
| Fix 7-layer → 8-layer in all docs | 🔲 Pending | 6 files affected |
| Update `.gitignore` | 🔲 Pending | Add model/env patterns |

---

### Phase 1: Benchmark Models & Measure Transliteration Tax (~4 hours)

| Task | Status | Notes |
|------|--------|-------|
| Install Python dependencies (`transformers`, `sacrebleu`, `ai4bharat-transliteration`) | 🔲 Pending | |
| Create `scripts/test_pretrained_models.py` | 🔲 Pending | Full script provided in plan |
| Run measurement (a): Marlish → Devanagari accuracy | 🔲 Pending | IndicXlit on 10 test sentences |
| Run measurement (b): Gold Devanagari → English BLEU | 🔲 Pending | opus-mt ceiling |
| Run measurement (c): End-to-end Marlish → English BLEU | 🔲 Pending | Full pipeline |
| Calculate transliteration tax: gap between (b) and (c) | 🔲 Pending | Leverage point diagnosis |

---

### Phase 2: Build IndicXlit Transliteration Pipeline (~3–4 days)

| Task | Status | Notes |
|------|--------|-------|
| Build token classifier (`scripts/transliterator/token_classifier.py`) | 🔲 Pending | English vs Marlish vs Devanagari vs Numeric |
| Build main pipeline (`scripts/transliterator/pipeline.py`) | 🔲 Pending | IndicXlit → freq-map → phoneme rules |
| Build fallback map loader (`scripts/transliterator/fallback_map.py`) | 🔲 Pending | Loads `transliteration_map.json` |
| Build phoneme rules (`scripts/transliterator/phoneme_rules.py`) | 🔲 Pending | Character-level last resort |
| Create module init (`scripts/transliterator/__init__.py`) | 🔲 Pending | |
| Build freq-map from parquet (`scripts/build_transliteration_map.py`) | 🔲 Pending | Extract from 3.6M rows |
| Port transliterator to JS (`lib/transliterator.js`) | 🔲 Pending | Freq-map + phoneme rules (no IndicXlit in browser) |
| Add `build-translit` npm script | 🔲 Pending | |
| Create `tests/test-transliterator.js` | 🔲 Pending | Automated test suite |
| Validate: accuracy ≥ 80% on Phase 1 test set | 🔲 Pending | |

---

### Phase 3: ONNX Export for Browser (~1 day)

| Task | Status | Notes |
|------|--------|-------|
| Install ONNX dependencies (`optimum`, `onnxruntime`) | 🔲 Pending | |
| Update `scripts/export_onnx.py` for opus-mt | 🔲 Pending | Change from mT5 to opus-mt-mr-en |
| Export to ONNX format | 🔲 Pending | |
| Quantize encoder + decoder to INT8 separately | 🔲 Pending | Target: < 75MB |
| Verify ONNX output matches PyTorch output | 🔲 Pending | Sanity check before browser integration |
| Copy quantized files to `public/models/opus-mt-mr-en/` | 🔲 Pending | |

---

### Phase 4: Browser Integration & Tier Router Update (~1.5 days)

| Task | Status | Notes |
|------|--------|-------|
| Update `lib/tier-router.js` for 3-tier architecture | 🔲 Pending | Preserve existing function signature |
| Install `@huggingface/transformers` (formerly `@xenova/transformers`) | 🔲 Pending | |
| Add model loading state to `useTranslation.js` | 🔲 Pending | Show loading indicator on first ONNX download |
| Update Service Worker (`sw.js`) cache list | 🔲 Pending | Add `transliteration_map.json` |
| Create `.env.local` for v1 | 🔲 Pending | API_ENDPOINT commented out |
| Validate: Tier 1 works (< 5ms) | 🔲 Pending | |
| Validate: Tier 3 ONNX works | 🔲 Pending | |
| Validate: Offline mode works | 🔲 Pending | |
| Validate: IndexedDB caches model | 🔲 Pending | |

---

### Phase 5: Benchmark, Demo Video & Documentation (~1.5 days)

| Task | Status | Notes |
|------|--------|-------|
| Create `scripts/evaluate_pipeline.py` | 🔲 Pending | Full measurement script provided in plan |
| Expand test set to 50+ sentences | 🔲 Pending | Source: `hinglish_marlish_v3_production_100k.json` |
| Measure: transliteration accuracy, BLEU, latency | 🔲 Pending | |
| Pass/fail check against targets | 🔲 Pending | BLEU ≥ 9, translit accuracy ≥ 75% |
| Record demo video (4 scenarios) | 🔲 Pending | Tier 1, Tier 3, offline, vs Google Translate |
| Update `README.md` with new claims and demo | 🔲 Pending | |
| Update `COLLABORATION.md` — remove training instructions | 🔲 Pending | |
| Update `docs/02-architecture.md` — reflect v1 architecture | 🔲 Pending | |

---

### Optional Phase (v2): Hosted API with IndicTrans2

| Task | Status | Notes |
|------|--------|-------|
| Create FastAPI server | ⏸️ Deferred | Do not attempt until v1 is shipped |
| Deploy to always-warm host | ⏸️ Deferred | Railway/Hetzner, not free HF Spaces |
| Set `NEXT_PUBLIC_API_ENDPOINT` and redeploy | ⏸️ Deferred | Tier-router already supports it |

---

## File Inventory

| File | Purpose | Status |
|------|---------|--------|
| `lib/dictionary-engine.js` | Core 8-layer rule-based NLP engine (Tier 1) | ✅ Active |
| `lib/tier-router.js` | Tier routing (cache → rules → ML) | ✅ Active (update in Phase 4) |
| `lib/transliterator.js` | Browser-side Marlish → Devanagari | 🔲 Phase 2 |
| `scripts/test_pretrained_models.py` | Phase 1 three-number benchmark | 🔲 Phase 1 |
| `scripts/build_transliteration_map.py` | Extract freq-map from parquet | 🔲 Phase 2 |
| `scripts/transliterator/pipeline.py` | Python transliteration orchestrator | 🔲 Phase 2 |
| `scripts/transliterator/token_classifier.py` | English vs Marlish classifier | 🔲 Phase 2 |
| `scripts/transliterator/fallback_map.py` | Loads transliteration_map.json | 🔲 Phase 2 |
| `scripts/transliterator/phoneme_rules.py` | Character-level last-resort rules | 🔲 Phase 2 |
| `scripts/export_onnx.py` | ONNX export (update for opus-mt) | ✅ Exists (update in Phase 3) |
| `scripts/evaluate_pipeline.py` | End-to-end v1 benchmark | 🔲 Phase 5 |
| `tests/test-transliterator.js` | JS transliterator tests | 🔲 Phase 2 |
| `docs/ARCHITECTURE_ANALYSIS_AND_PLAN.md` | Full pivot analysis & plan | ✅ Active |

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| Dataset merging complete (all sources) | 2026-05-04 | ✅ Done |
| mT5 training diagnosed (BLEU ~3) | 2026-05-18 | ✅ Done |
| Pivot plan finalized & approved | 2026-05-23 | ✅ Done |
| Phase 0: Archive & cleanup | 2026-05-24 | 🔲 Pending |
| Phase 1: Three-number benchmark | 2026-05-25 | 🔲 Pending |
| Phase 2: Transliteration pipeline | 2026-05-29 | 🔲 Pending |
| Phase 3: ONNX export & quantization | 2026-05-30 | 🔲 Pending |
| Phase 4: Browser integration | 2026-06-01 | 🔲 Pending |
| Phase 5: Benchmark, demo, docs | 2026-06-03 | 🔲 Pending |
| **v1 Portfolio-Ready** | **2026-06-03** | 🔲 Pending |
