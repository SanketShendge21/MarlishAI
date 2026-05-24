---
title: Marlish.AI — Progress Tracker
updated: 2026-05-24
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
**Status: 🔲 In Progress (Started May 24, 2026)**
- [x] Create `scripts/transliterator/token_classifier.py`. *(Classifies tokens as ENGLISH/DEVANAGARI/NUMERIC/MARLISH. ~80 English loanwords in passthrough set.)*
- [x] Create `scripts/transliterator/phoneme_rules.py`. *(Character-level Romanized→Devanagari rules. ~50 rules. Fixed ordering bug: `chh` now before `ch` to prevent partial match.)*
- [x] Create `scripts/transliterator/fallback_map.py`. *(~170 curated Marlish→Devanagari entries. Merges with auto-generated dataset map at runtime.)*
- [x] Create `scripts/transliterator/pipeline.py` + `__init__.py`. *(3-tier orchestrator: IndicXlit → Fallback Map → Phoneme Rules. Tracks per-tier hit stats.)*
- [x] Create `scripts/build_transliteration_map.py`. *(Auto-detects columns, extracts word pairs via naive alignment, frequency-ranked, capped at 10k entries. Also processes JSON dictionaries.)*
- [x] Create `requirements.txt` + `SETUP_ML.md`. *(Full setup guide for second machine. torch excluded from requirements — CUDA/CPU varies.)*
- [x] Moved `docs/Dictionary_Refs/` → `datasets/`. Updated all active file paths (`build_transliteration_map.py`, `build-dictionary.js`, `inspect_parquet.py`, `.gitignore`).
- [ ] Run `build_transliteration_map.py` and generate `public/transliteration_map.json`.
- [ ] Test pipeline against 50+ real Marlish sentences and document accuracy.

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

*(Future phases will be added here as they become active.)*
