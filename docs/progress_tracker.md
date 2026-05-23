---
title: Marlish.AI — Progress Tracker
updated: 2026-05-23
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

We have pivoted to a **Hybrid Transliteration-First Architecture** utilizing pre-trained models (`opus-mt` for browser, `IndicTrans2` for API) combined with a custom Marlish → Devanagari transliteration pipeline.

### Phase 0: Archive & Cleanup
**Status: ✅ COMPLETE (May 23, 2026)**
- Created `pre-pivot-mt5-training` archive branch.
- Moved old training scripts to `legacy/scripts/`.
- Moved old models to `legacy/models/`.
- Deleted 18.4M-row `ml_splits` to save space.
- Fixed 7-layer → 8-layer terminology across all documentation.
- Updated `.gitignore` for Python environments and legacy models.

### Phase 1: Benchmark Models & Measure Transliteration Tax
**Status: 🔲 In Progress**
- [ ] Set up Python virtual environment (`venv`).
- [ ] Install dependencies (`transformers`, `torch`, `sacrebleu`, `ai4bharat-transliteration`).
- [ ] Create `test_pretrained_models.py` benchmark script.
- [ ] Measure pure Devanagari → English BLEU (Quality Ceiling).
- [ ] Measure End-to-End Marlish → English BLEU.

---

*(Future phases will be added here as they become active.)*
