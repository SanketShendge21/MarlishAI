---
title: Marlish.AI — ML/NLP Model Progress Tracker
updated: 2026-05-04
---

# Marlish.AI — ML/NLP Model Progress Tracker

> Tracks progress across all phases of the custom ML/NLP model development roadmap.

---

## Phase 1: Data Preparation

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
| Add Hindi (Devanagari) alphabet ↔ English mappings | ✅ Done | 58 character mappings (vowels + consonants + numbers) |
| Add Marathi (Devanagari) alphabet ↔ English mappings | ✅ Done | 59 character mappings (vowels + consonants + ळ + numbers) |
| Remove duplicates & normalize text | ✅ Done | Dedup across all sources |
| Merge all into `Combined_Parallel_Dataset.csv` | ✅ Done | ~8.5M+ total rows before dedup |

### 1b. Data Splitting

| Task | Status | Notes |
|------|--------|-------|
| Create train/val/test splits (80/10/10) | 🔲 Pending | Script: `scripts/data_preprocessing.py` |
| Generate parallel pairs: Hinglish → English | 🔲 Pending | With direction prefixes |
| Generate parallel pairs: Marlish → English | 🔲 Pending | With direction prefixes |
| Generate parallel pairs: Hindi → English | 🔲 Pending | With direction prefixes |
| Generate parallel pairs: Marathi → English | 🔲 Pending | With direction prefixes |
| Save splits to `docs/Dictionary_Refs/ml_splits/` | 🔲 Pending | train.csv, val.csv, test.csv |

### 1c. Data Augmentation (Optional)

| Task | Status | Notes |
|------|--------|-------|
| Expand with typo variants from typo-map.js | 🔲 Pending | Low priority, can do post-v1 |
| Add slang/abbreviation variants | 🔲 Pending | From JSON dictionaries |

---

## Phase 2: Model Selection & Training

### 2a. Model Choice

| Task | Status | Notes |
|------|--------|-------|
| Select model architecture | ✅ Done | `google/mt5-small` — multilingual T5, ONNX-compatible |
| Verify Transformers.js compatibility | ✅ Done | mT5 is supported by Transformers.js |

### 2b. Training Pipeline

| Task | Status | Notes |
|------|--------|-------|
| Install training dependencies | 🔲 Pending | `torch`, `transformers`, `sentencepiece`, `datasets`, `evaluate`, `sacrebleu` |
| Create training script | ✅ Done | `scripts/train_model.py` |
| Fine-tune mT5-small on parallel data | 🔲 Pending | 3 epochs, batch size 8, lr=5e-5 |
| Monitor BLEU/ROUGE on validation set | 🔲 Pending | Built into training loop |
| Save best model checkpoint | 🔲 Pending | Auto-save at `models/marlish_mt5_finetuned/` |

### 2c. Export & Quantization

| Task | Status | Notes |
|------|--------|-------|
| Export model to ONNX format | 🔲 Pending | Script: `scripts/export_onnx.py` |
| Quantize to INT8 | 🔲 Pending | Target: <40MB |
| Verify ONNX model accuracy | 🔲 Pending | Compare BLEU scores |

---

## Phase 3: Integration with Marlish.AI Pipeline

### 3a. ML Fallback Logic

| Task | Status | Notes |
|------|--------|-------|
| Add confidence threshold to dictionary-engine.js | 🔲 Pending | If rule-based confidence < threshold → call ML model |
| Implement ML inference function in JS | 🔲 Pending | Using Transformers.js or ONNX.js |

### 3b. Browser Inference

| Task | Status | Notes |
|------|--------|-------|
| Load quantized model in browser | 🔲 Pending | Via Transformers.js |
| Implement lazy-loading for ML model | 🔲 Pending | Only load when needed |
| Add IndexedDB caching for offline use | 🔲 Pending | Cache model weights locally |

### 3c. Preprocessing

| Task | Status | Notes |
|------|--------|-------|
| Run typo normalization before ML inference | 🔲 Pending | Use existing typo-map.js |
| Run grammar reordering before ML inference | 🔲 Pending | Use existing grammar-rules.js |

---

## Phase 4: Testing & Evaluation

### 4a. Automated Tests

| Task | Status | Notes |
|------|--------|-------|
| Create evaluation script | ✅ Done | `scripts/evaluate_model.py` |
| Create test cases for hard/ambiguous sentences | 🔲 Pending | Focus on code-mixed Hinglish/Marlish |
| Compare: dictionary-only vs hybrid vs ML-only | 🔲 Pending | Side-by-side comparison |
| Measure BLEU scores by direction | 🔲 Pending | Hinglish→En, Marlish→En, Hindi→En, Marathi→En |

### 4b. User Feedback Loop

| Task | Status | Notes |
|------|--------|-------|
| Log user corrections for retraining | 🔲 Pending | Store corrections in local DB |
| Implement feedback collection UI | 🔲 Pending | Thumbs up/down on translations |

---

## Phase 5: Deployment & Optimization

### 5a. Bundle Model Efficiently

| Task | Status | Notes |
|------|--------|-------|
| Lazy-load ML model only when needed | 🔲 Pending | After dictionary-engine fails |
| Cache model in IndexedDB | 🔲 Pending | Offline-first architecture |
| Optimize model loading time | 🔲 Pending | Target: <3s on first load |

### 5b. Monitor Performance

| Task | Status | Notes |
|------|--------|-------|
| Track inference latency | 🔲 Pending | Target: <500ms per translation |
| Track memory usage | 🔲 Pending | Target: <100MB browser memory |
| Track translation accuracy | 🔲 Pending | Via user feedback metrics |

---

## Phase 6: Documentation & Maintenance

### 6a. Document the Hybrid Flow

| Task | Status | Notes |
|------|--------|-------|
| Update architecture docs | 🔲 Pending | Explain hybrid pipeline |
| Document ML model specs | 🔲 Pending | Model size, accuracy, latency |

### 6b. Continuous Data Expansion

| Task | Status | Notes |
|------|--------|-------|
| Plan data collection pipeline | 🔲 Pending | User corrections → retraining |
| Schedule periodic retraining | 🔲 Pending | Monthly or on-demand |

---

## File Inventory

| File | Purpose |
|------|---------|
| `scripts/combine_datasets.py` | Merges all data sources into Combined_Parallel_Dataset.csv |
| `scripts/data_preprocessing.py` | Cleans data and creates train/val/test splits |
| `scripts/train_model.py` | Fine-tunes mT5-small on parallel corpus |
| `scripts/export_onnx.py` | Exports trained model to ONNX + INT8 quantization |
| `scripts/evaluate_model.py` | Evaluates model with BLEU scores and sample translations |
| `docs/ml_nlp_model_roadmap.md` | Original roadmap document |
| `docs/progress_tracker.md` | This file — tracks progress |

---

## Milestones

| Milestone | Target Date | Status |
|-----------|------------|--------|
| Dataset merging complete (all sources) | 2026-05-04 | ✅ Done |
| Hindi/Marathi Devanagari alphabets added | 2026-05-04 | ✅ Done |
| Data preprocessing & splits | 2026-05-04 | 🔲 Pending |
| Model training (mT5-small, 3 epochs) | 2026-05-05 | 🔲 Pending |
| ONNX export + quantization | 2026-05-05 | 🔲 Pending |
| Browser integration (Transformers.js) | 2026-05-06 | 🔲 Pending |
| Testing & evaluation | 2026-05-06 | 🔲 Pending |
| Production deployment | 2026-05-07 | 🔲 Pending |

---

## Quick Commands

```bash
# Step 1: Rebuild the combined dataset (merges all CSVs + JSONs + Parquets + alphabets)
python scripts/combine_datasets.py

# Step 2: Preprocess data and create train/val/test splits
python scripts/data_preprocessing.py

# Step 3: Install ML dependencies
pip install torch transformers sentencepiece datasets evaluate sacrebleu scikit-learn

# Step 4: Train the model
python scripts/train_model.py

# Step 5: Export to ONNX and quantize
pip install optimum[onnxruntime] onnx onnxruntime
python scripts/export_onnx.py

# Step 6: Evaluate
python scripts/evaluate_model.py
```
