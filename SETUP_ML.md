# MarlishAI — ML Pipeline Setup Guide

> Quick setup guide for the Python/ML side of MarlishAI. Follow these steps to get the transliteration pipeline and model benchmarking running on a new machine.

---

## Prerequisites

- **Python 3.11+** (tested on 3.13.3)
- **Node.js 18+** (for the Next.js frontend)
- **GPU (optional but recommended):** NVIDIA GPU with CUDA support (tested on RTX 3060)

---

## 1. Clone & Switch Branch

```bash
git clone https://github.com/SanketShendge21/MarlishAI.git
cd MarlishAI
git checkout Dev-Branch
```

---

## 2. Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

---

## 3. Install Dependencies

### With GPU (NVIDIA CUDA):
```bash
# Install PyTorch with CUDA first (adjust cu124 to your CUDA version)
pip install torch --index-url https://download.pytorch.org/whl/cu124

# Install remaining dependencies
pip install -r requirements.txt
```

### CPU Only:
```bash
pip install torch
pip install -r requirements.txt
```

### Verify GPU detection:
```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else 'CPU only')"
```

---

## 4. Dataset Setup

The `datasets/` folder should contain the following files. These are **not committed to git** (too large) — copy them manually from your other machine or download from the original sources.

### Required Files:

| File | Size | Contents |
|------|------|----------|
| `Marathi_part_1.parquet` | ~244 MB | 1.8M rows — Marathi Devanagari + English |
| `Marathi_part_2.parquet` | ~244 MB | 1.8M rows — Marathi Devanagari + English |
| `Hinglish_part_1.parquet` | ~125 MB | 500K rows — Hinglish + Hindi Devanagari + English |
| `Hinglish_part_2.parquet` | ~106 MB | 500K rows — Hinglish + Hindi Devanagari + English |
| `hinglish_marlish_10000_dataset.json` | ~2.4 MB | Word-level dictionary (v1) |
| `hinglish_marlish_v2_25000_dataset.json` | ~6.8 MB | Phrase-level dictionary (v2) |
| `hinglish_marlish_v3_production_100k.json` | ~39.5 MB | Production dictionary (v3) |
| `marlish_ai_5000_premium_dataset.json` | ~1.7 MB | Premium curated dataset |

### Optional Files:
| File | Size | Notes |
|------|------|-------|
| `Combined_Parallel_Dataset.csv` | ~2.4 GB | Full merged dataset (not needed for current pipeline) |

---

## 5. Running Scripts

### Build the transliteration map (extracts word pairs from parquet data):
```bash
python scripts/build_transliteration_map.py
# Output: public/transliteration_map.json
```

### Test the transliteration pipeline:
```bash
python -m scripts.transliterator.pipeline
```

### Run the model benchmark:
```bash
python scripts/test_pretrained_models.py
# Tests opus-mt-mr-en with both transliterated and gold Devanagari input
# Outputs BLEU scores and transliteration tax measurement
```

### Build the NLP dictionary (JS):
```bash
node scripts/build-dictionary.js
# Output: public/dictionary.json
```

---

## 6. Project Structure (ML-related files)

```
MarlishAI/
├── datasets/                          # Source datasets (NOT in git)
│   ├── Marathi_part_1.parquet
│   ├── Marathi_part_2.parquet
│   ├── Hinglish_part_1.parquet
│   ├── Hinglish_part_2.parquet
│   └── *.json                         # Dictionary JSON files
├── scripts/
│   ├── test_pretrained_models.py      # Phase 1: Model benchmarking
│   ├── build_transliteration_map.py   # Phase 2: Extract frequency map
│   ├── build-dictionary.js            # NLP dictionary builder
│   └── transliterator/                # Phase 2: Transliteration pipeline
│       ├── __init__.py
│       ├── pipeline.py                # 3-tier orchestrator
│       ├── token_classifier.py        # English/Marlish/Devanagari classifier
│       ├── fallback_map.py            # ~170 curated word mappings
│       └── phoneme_rules.py           # Character-level last-resort rules
├── public/
│   ├── dictionary.json                # Built NLP dictionary
│   └── transliteration_map.json       # Built frequency map (after running script)
├── requirements.txt                   # Python dependencies
├── venv/                              # Virtual environment (NOT in git)
└── docs/
    ├── progress_tracker.md            # Current project status
    └── ARCHITECTURE_ANALYSIS_AND_PLAN.md  # Master plan
```

---

## 7. Current Status

See `docs/progress_tracker.md` for the latest project status.

**Key finding from Phase 1:** `Helsinki-NLP/opus-mt-mr-en` is NOT suitable for conversational Marathi (trained on religious text, hallucinates). IndicTrans2 investigation is pending.

---

## Troubleshooting

### `torch.cuda.is_available()` returns False
- Ensure you installed the CUDA version: `pip install torch --index-url https://download.pytorch.org/whl/cu124`
- Check your CUDA version: `nvidia-smi` (look for "CUDA Version" in top right)
- Python 3.13 may need `cu124` or `cu126` (not `cu121`)

### `ImportError: pyarrow is required for parquet support`
- Run: `pip install pyarrow`

### PowerShell `Activate.ps1` error
- Don't prefix with `python`: use `.\venv\Scripts\activate` (not `python .\venv\Scripts\activate`)
