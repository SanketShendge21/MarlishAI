---
title: Marlish.AI — ML/NLP Model Progress Tracker
updated: 2026-05-05
---

# Marlish.AI — ML/NLP Model Progress Tracker

> Tracks progress across all phases of the custom ML/NLP model development roadmap.
> This file is the single source of truth for what has been done, what is in progress, and what is pending.

---

## System & Environment Details

| Item | Value |
|------|-------|
| **GPU** | NVIDIA RTX 3060 (12GB VRAM, Compute Capability 8.6) |
| **Python** | 3.13 |
| **PyTorch** | 2.6.0+cu124 (CUDA 12.4 — installed via `pip install torch --index-url https://download.pytorch.org/whl/cu124`) |
| **Model** | `google/mt5-small` (mT5, ~300M parameters, multilingual Seq2Seq) |
| **Dataset** | `Combined_Parallel_Dataset.csv` — ~8.26 million rows across 5 columns |
| **Training Approach** | GPU fine-tuning with FP16 mixed precision, checkpoint resume support |
| **Translation Directions** | Bidirectional: Hinglish ↔ English, Marlish ↔ English, Hindi ↔ English, Marathi ↔ English (8 directions total) |

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
| Remove duplicates & normalize text | ✅ Done | Dedup across all sources via `combine_datasets.py` step 7 |
| Merge all into `Combined_Parallel_Dataset.csv` | ✅ Done | **8,264,720 final rows** after dedup |

**Important Note:** The Hinglish parquet data (both parts, ~1M rows total) IS included in the Combined Dataset. It appears near the bottom of the 8.2M rows (after the Marathi parquet data). The preprocessing script shuffles randomly, so all directions are evenly mixed in the ML splits.

### 1b. Data Splitting (Bidirectional)

| Task | Status | Notes |
|------|--------|-------|
| Create train/val/test splits (80/10/10) | ✅ Done | Completed 2026-05-05 |
| Generate bidirectional pairs: Hinglish ↔ English | ✅ Done | 2,013,398 pairs (both directions) |
| Generate bidirectional pairs: Marlish ↔ English | ✅ Done | 7,227,028 pairs (both directions) |
| Generate bidirectional pairs: Hindi ↔ English | ✅ Done | 2,003,282 pairs (both directions) |
| Generate bidirectional pairs: Marathi ↔ English | ✅ Done | 14,486,832 pairs (both directions) |
| Deduplicate globally | ✅ Done | Removed 7,246,849 duplicates |
| Save splits to `docs/Dictionary_Refs/ml_splits/` | ✅ Done | train.csv, val.csv, test.csv |

**Final preprocessing stats (2026-05-05):**
- **Total unique pairs: 18,483,691** (across 8 translation directions)
- Train: 14,786,952 | Val: 1,848,369 | Test: 1,848,370
- Train distribution:
  - `marathi_to_english`: 5,795,175 | `english_to_marlish`: 2,891,335 | `marlish_to_english`: 2,890,500
  - `english_to_hinglish`: 805,093 | `hinglish_to_english`: 804,872
  - `english_to_hindi`: 799,912 | `hindi_to_english`: 799,518
  - `english_to_marathi`: 547 (very few — most Marathi data lacks reverse mapping)

> **Note:** `english_to_marathi` has very few pairs because the Marathi parquets only contain `src`(Marathi)→`tgt`(English) columns without reverse data in the Combined Dataset. The Marlish column covers Marathi→English transliteration well.

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
| Select model architecture | ✅ Done | `google/mt5-small` (300M params) — powerful multilingual Seq2Seq |
| Verify Transformers.js compatibility | ✅ Done | mT5 is supported by Transformers.js for browser inference |

**Architecture Decision Log:**
- Initially considered `Helsinki-NLP/opus-mt-mul-en` (MarianMT, 74M params) for CPU training
- Switched to `google/mt5-small` (300M params) after user confirmed RTX 3060 GPU availability
- mT5 has much better multilingual understanding and context awareness for custom dialects like Hinglish/Marlish

### 2b. Training Pipeline

| Task | Status | Notes |
|------|--------|-------|
| Install PyTorch with CUDA 12.4 | ✅ Done | `torch 2.6.0+cu124` installed for Python 3.13 compatibility |
| Install other training dependencies | ✅ Done | `transformers`, `sentencepiece`, `evaluate`, `sacrebleu`, `accelerate>=1.1.0` |
| Create training script | ✅ Done | `scripts/train_model.py` — GPU-optimized with FP16 & auto-resume |
| Fine-tune mT5-small on parallel data | ⏳ Next Step | Data ready! Run `python scripts/train_model.py` to start |
| Monitor BLEU/ROUGE on validation set | ⏳ Awaiting | Built into training loop (`compute_metrics`) |
| Save best model checkpoint | ⏳ Awaiting | Auto-save at `models/marlish_mt5_finetuned/`, keeps last 2 checkpoints |

**Training Strategy (2-stage):**
1. **Stage 1 (Pipeline Validation):** Train on 500k balanced subset (~62.5k per direction, ~3-4 hours on RTX 3060). Purpose: Verify the entire pipeline works end-to-end (train → export → browser integration). If BLEU scores look reasonable and the ONNX export succeeds, we know the pipeline is solid.
2. **Stage 2 (Full Training):** Change `MAX_TRAIN_SAMPLES = None` in `train_model.py` and train on all 14.7M training pairs. This will take ~40-60 hours total but can be done across multiple sessions using checkpoint resume. This produces the production-quality model.

**Training Configuration:**

| Parameter | Value | Reason |
|-----------|-------|--------|
| Batch Size | 16 | Safe for 12GB VRAM with mT5 (300M params) |
| Epochs | 3 | Standard for fine-tuning Seq2Seq models |
| Learning Rate | 3e-5 | Standard for mT5 fine-tuning |
| Warmup Steps | 500 | Gradual LR ramp-up to prevent instability |
| Eval Steps | 1,000 | Evaluate BLEU every 1k steps |
| Eval Steps | 500 | Evaluate BLEU every 500 steps |
| Save Steps | 1,000 | Checkpoint every 1k steps (resumable) |
| Grad Accumulation | 2 | Effective batch = 16 × 2 = 32 |
| Max Sequence Length | 128 tokens | Covers most sentences in our dataset |
| ~~FP16~~ | ~~Disabled~~ | ~~mT5 overflows in fp16 → loss=0, grad=NaN~~ |
| **BF16** | Auto (True if Ampere+) | mT5 was pre-trained with bfloat16; RTX 3060 supports it natively |
| Initial Sample Size | 500,000 | Balanced across 8 directions (62.5k each) |

**Key Features in `train_model.py`:**
- ✅ Dynamic direction prefixes (e.g., `translate Hinglish to English: `) — auto-parsed from dataset
- ✅ Balanced sampling across all translation directions
- ✅ Automatic checkpoint resume — can stop/start training safely
- ✅ **BF16 mixed precision** — mT5-compatible (fp16 was causing loss=0 bug)
- ✅ Test BLEU evaluation after training completes
- ✅ Sample translations printed at end for quick quality check

#### 📊 Training Checkpoint Tracker
*Since full training spans multiple hours/days, use this log to track resumed sessions.*

| Session # | Date | Run Target | Starting Checkpoint | Ending Checkpoint | Steps | Loss | BLEU | Notes |
|-----------|------|------------|---------------------|-------------------|-------|------|------|-------|
| 1 | 2026-05-08 | 500k subset | Fresh start (0) | `checkpoint-6000` | 6000 | 0 | 0 | ❌ FAILED — fp16 caused loss=0 / grad_norm=NaN. Checkpoints corrupted. |
| 2 | TBD | 500k subset | Fresh start (0) | TBD | - | - | - | 🔄 Retry with bf16 fix. Must delete old checkpoints first! |
| 3 | TBD | Full dataset | Resume from #2 | TBD | - | - | - | Full training continuation |

### 2c. Export & Quantization

| Task | Status | Notes |
|------|--------|-------|
| Export model to ONNX format | 🔲 Pending | Script: `scripts/export_onnx.py` — ready to run after training |
| Quantize to INT8 | 🔲 Pending | Target: <40MB for browser deployment |
| Verify ONNX model accuracy | 🔲 Pending | Compare BLEU scores: PyTorch vs ONNX |

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
| Measure BLEU scores by direction | 🔲 Pending | All 8 directions separately |

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

| File | Purpose | Status |
|------|---------|--------|
| `scripts/combine_datasets.py` | Merges ALL data sources (CSVs + JSONs + Parquets + alphabets) into `Combined_Parallel_Dataset.csv` | ✅ Working |
| `scripts/data_preprocessing.py` | Cleans data, creates bidirectional pairs (8 directions), splits into train/val/test (80/10/10) | ✅ Working (memory-optimized) |
| `scripts/train_model.py` | Fine-tunes mT5-small on parallel corpus with GPU/FP16 support and checkpoint resume | ⚠️ Has 2 minor issues to fix (see below) |
| `scripts/export_onnx.py` | Exports trained model to ONNX + INT8 quantization for browser deployment | ✅ Ready (run after training) |
| `scripts/evaluate_model.py` | Evaluates model with BLEU scores and sample translations per direction | ⚠️ Has 1 issue to fix (see below) |
| `docs/ml_nlp_model_roadmap.md` | Original 6-phase roadmap document | ✅ Reference doc |
| `docs/progress_tracker.md` | **This file** — tracks all progress | ✅ Active |

---

## Known Issues to Fix

### Issue 1: `train_model.py` — Stale docstring and banner
- **Lines 1-6, 126:** The docstring still says "CPU-Optimized" and references MarianMT. Should say "GPU-Optimized" and reference mT5-small.
- **Line 272:** Sample translations section uses old `>>eng<<` prefix instead of new dynamic `translate X to Y:` format
- **Severity:** Low (cosmetic + sample translations will use wrong prefix at end)

### Issue 2: `train_model.py` — Balanced sampling divides by 4, not 8
- **Line 144:** `per_dir = MAX_TRAIN_SAMPLES // 4` should be `// train_df['direction'].nunique()` since we now have 8 directions, not 4.
- **Severity:** Medium (will sample 125k per direction instead of 62.5k, totaling 1M instead of 500k)

### Issue 3: `evaluate_model.py` — Hardcoded prefix map (only 4 directions)
- **Lines 26-32:** Uses a hardcoded `prefix_map` with only 4 X→English directions. Missing the 4 English→X directions.
- **Severity:** Medium (evaluation won't work for reverse translations)

---

## Milestones

| Milestone | Target Date | Status |
|-----------|------------|--------|
| Dataset merging complete (all sources) | 2026-05-04 | ✅ Done |
| Hindi/Marathi Devanagari alphabets added | 2026-05-04 | ✅ Done |
| Data preprocessing & bidirectional splits | 2026-05-05 | 🔄 Needs Re-run |
| PyTorch CUDA 12.4 installed | 2026-05-05 | ✅ Done |
| Model training (mT5-small, 500k, 3 epochs) | 2026-05-05 | ⏳ Awaiting |
| ONNX export + quantization | After training | 🔲 Pending |
| Browser integration (Transformers.js) | After export | 🔲 Pending |
| Testing & evaluation | After integration | 🔲 Pending |
| Production deployment | After testing | 🔲 Pending |

---

## Quick Commands (Run in Order)

```bash
# ──── STEP 1: Verify GPU is working ────
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

# ──── STEP 2: Generate bidirectional ML training splits ────
python scripts/data_preprocessing.py

# ──── STEP 3: Train the model (500k subset, ~3-4 hours on RTX 3060) ────
python scripts/train_model.py

# ──── STEP 4: Export to ONNX and quantize (after training completes) ────
pip install optimum[onnxruntime] onnx onnxruntime
python scripts/export_onnx.py

# ──── STEP 5: Evaluate model quality ────
python scripts/evaluate_model.py
```

**Notes:**
- Training can be stopped with `Ctrl+C` and resumed later — checkpoints are saved every 2,000 steps
- The model does NOT need to be retrained after deployment — the trained weights are frozen
- ONNX export produces a browser-ready model file that runs entirely client-side
