---
title: Marlish.AI — ML/NLP Model Progress Tracker
updated: 2026-05-20
---

# Marlish.AI — ML/NLP Model Progress Tracker

> Tracks progress across all phases of the custom ML/NLP model development roadmap.
> This file is the single source of truth for what has been done, what is in progress, and what is pending.

---

## ⚠️ STRATEGIC PIVOT (May 2026)
Following an evaluation of the `mT5-small` scratch training attempt (which yielded a BLEU score of ~3), the project has officially pivoted to a **Hybrid Transliteration-First Architecture**. Scratch training was abandoned due to the low output quality ceiling and high compute cost. We are adopting pre-trained models (`opus-mt` and `IndicTrans2`) combined with a custom Marlish → Devanagari transliteration pipeline.

---

## System & Environment Details

| Item | Value |
|------|-------|
| **Core NLP Engine** | 8-Layer JavaScript Rule Engine (Tier 1) |
| **Offline ML Fallback** | `Helsinki-NLP/opus-mt-mr-en` (ONNX INT8 Quantized, target <75MB) - *New Stack* |
| **Online ML API** | `IndicTrans2` or `opus-mt` (Hosted via API) - *New Stack* |
| **Transliteration** | Custom phoneme-to-grapheme pipeline (Marlish → Devanagari) - *New Core Feature* |
| **Legacy Model (Abandoned)** | `google/mt5-small` (Yielded BLEU ~3, insufficient for demo) |

---

## Phase 1: Data Preparation (Legacy/Retained)

### 1a. Data Extraction & Cleaning

| Task | Status | Notes |
|------|--------|-------|
| Parse `apni_bhasha_100k_training_dataset.csv` | ✅ Done | 100,000 rows — Hinglish/Marlish/Hindi/Marathi/English |
| Parse `Apni_Bhasha_Dataset.csv` | ✅ Done | 496 rows — basic parallel pairs |
| Parse `Apni_Bhasha_Marlish_Dataset.csv` | ✅ Done | 3,627,480 rows — Marathi/Marlish/English |
| Parse JSON dictionaries (4 files) | ✅ Done | 140,000 rows from Hinglish/Marlish word dictionaries |
| Parse `Hinglish_part_1.parquet` | ✅ Done | 500,662 rows — Hinglish + Hindi Devanagari + English |
| Parse `Hinglish_part_2.parquet` | ✅ Done | 500,661 rows — Hinglish + Hindi Devanagari + English |
| Parse `Marathi_part_1.parquet` | ✅ Done | 1,813,740 rows — Marathi Devanagari + English |
| Parse `Marathi_part_2.parquet` | ✅ Done | 1,813,740 rows — Marathi Devanagari + English |
| Add Hindi/Marathi alphabets ↔ English mappings | ✅ Done | |
| Remove duplicates & normalize text | ✅ Done | Dedup across all sources via `combine_datasets.py` |
| Merge all into `Combined_Parallel_Dataset.csv` | ✅ Done | **8,264,720 final rows** after dedup |

### 1b. Data Splitting (Bidirectional) - *Partially Abandoned*

| Task | Status | Notes |
|------|--------|-------|
| Create train/val/test splits (80/10/10) | 🚫 Skipped | ML splits deleted. No longer training a model from scratch. Keeping source CSVs for transliteration map. |
| Generate bidirectional pairs | 🚫 Skipped | No longer training a bidirectional model. |
| Deduplicate globally | ✅ Done | Retained for transliteration dataset building. |

---

## Phase 2: Legacy Model Selection & Training (Abandoned)

| Task | Status | Notes |
|------|--------|-------|
| Select model architecture | 🚫 Abandoned | Originally `mT5-small`. Abandoned because scratch training yielded BLEU ~3. Switched to pretrained `opus-mt` and `IndicTrans2`. |
| Install training dependencies & PyTorch | ✅ Done | Environment was successfully set up. |
| Fine-tune mT5-small on parallel data | 🚫 Abandoned | Stopped after pipeline validation showed ~3 BLEU. Compute cost not worth the low quality. |
| Monitor BLEU/ROUGE on validation set | 🚫 Abandoned | Initial results too low to continue. |
| Save best model checkpoint | 🚫 Abandoned | Checkpoints deleted to free up disk space. |

---

## NEW Phase 3: Transliteration & Pre-Trained Models (Strategic Pivot)

| Task | Status | Notes |
|------|--------|-------|
| Benchmark `opus-mt-mr-en` and `IndicTrans2` | 🔲 Pending | Evaluate model quality with transliterated input. |
| Build English vs. Marlish token classifier | 🔲 Pending | Core component for transliteration. |
| Extract phonetic mappings from Marlish parquet | 🔲 Pending | Use existing 3.6M row dataset. |
| Handle hard transliteration cases | 🔲 Pending | English loanwords, ambiguity, regional variants. |
| Validate transliterator accuracy | 🔲 Pending | Target: >85% accuracy on 50+ WhatsApp-style Marlish sentences. |

---

## NEW Phase 4: Export & Browser Integration

| Task | Status | Notes |
|------|--------|-------|
| Export `opus-mt-mr-en` to ONNX | 🔲 Pending | For offline browser fallback. |
| Quantize to INT8 | 🔲 Pending | Target: <75MB. |
| Port transliteration map to JS | 🔲 Pending | Create `lib/transliterator.js`. |
| Implement lazy-loading for ONNX model | 🔲 Pending | Only load on first offline Tier 2 request. |
| Update `lib/tier-router.js` for Hybrid architecture | 🔲 Pending | Route: Tier 1 (Rules) -> Tier 2 API (Online) -> Tier 2 ONNX (Offline). |

---

## NEW Phase 5: Hosted API Deployment

| Task | Status | Notes |
|------|--------|-------|
| Create FastAPI server (`api/app.py`) | 🔲 Pending | Integrate transliteration pipeline and ML model. |
| Deploy to Hugging Face Spaces | 🔲 Pending | Expose `/translate` endpoint. |
| Test API endpoint from browser | 🔲 Pending | Verify latency <500ms. |

---

## Phase 6: Benchmarking, Demo & Documentation

| Task | Status | Notes |
|------|--------|-------|
| Create end-to-end pipeline benchmark script | 🔲 Pending | Test Marlish → Transliterate → Translate. |
| Measure Tier 1 hit rate, Transliteration accuracy, BLEU | 🔲 Pending | |
| Record demo video for portfolio | 🔲 Pending | Highlight fast Tier 1, ML Tier 2, and Offline mode. |
| Finalize `README.md` and architecture documentation | 🔲 Pending | |

---

## File Inventory (Updated)

| File | Purpose | Status |
|------|---------|--------|
| `lib/dictionary-engine.js` | Core 8-layer rule-based NLP engine (Tier 1) | ✅ Active |
| `scripts/train_model.py` | Legacy mT5 training script | ❌ Deleted (Obsolete) |
| `scripts/data_preprocessing.py` | Legacy data splitting | ❌ Deleted (Obsolete) |
| `scripts/build_transliteration_map.py`| Extracts mappings from source datasets | 🔲 Planned |
| `scripts/transliterator/pipeline.py` | Main transliteration orchestrator | 🔲 Planned |
| `scripts/test_pretrained_models.py` | Benchmarks pretrained models | 🔲 Planned |
| `api/app.py` | Hosted FastAPI server for Tier 2 | 🔲 Planned |
| `docs/ARCHITECTURE_ANALYSIS_AND_PLAN.md`| Deep analysis & pivot plan | ✅ Active |

---

## Milestones

| Milestone | Target Date | Status |
|-----------|------------|--------|
| Dataset merging complete (all sources) | 2026-05-04 | ✅ Done |
| Model training (mT5-small, 500k, 3 epochs) | N/A | 🚫 Abandoned (BLEU too low, pivoted) |
| Delete obsolete ML split files & checkpoints | 2026-05-20 | ✅ Done |
| Develop Transliteration Pipeline | TBD | 🔲 Pending |
| Test Pretrained Models | TBD | 🔲 Pending |
| ONNX export + quantization | TBD | 🔲 Pending |
| Browser integration (Transformers.js) | TBD | 🔲 Pending |
