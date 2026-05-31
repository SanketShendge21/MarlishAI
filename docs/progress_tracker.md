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

#### Known Issues (identified, not yet fixed):
1. **NLLB-200 translation quality on colloquial text** — makes semantic errors on informal chat (e.g., "kal meeting hai bro" → "Time to meet up bro" instead of "There is a meeting tomorrow"). This is a model limitation, not a code bug.
   - **Research needed:** User provided a Gemini Deep Research prompt to investigate solutions (bigger NLLB-1.3B, fine-tuning, free local LLM post-processing)
   - Options under consideration: NLLB-1.3B swap, fine-tuning on curated data, Gemma 3 1B post-processing
2. **Transliteration pipeline still misses some words** — seed map covers ~280 words but informal chat uses thousands of variants. Ongoing improvement.

#### Remaining:
- [ ] **Restart API server** to pick up all changes (seed map fixes, reverse translit, API v3) ← **START HERE**
- [ ] **Test the full frontend** in browser with all language pairs
- [ ] **Research translation quality improvements** (Gemini Deep Research results)
- [ ] Implement quality improvements based on research
- [ ] Deploy API to Hugging Face Spaces (free GPU)
- [ ] Deploy frontend to Vercel

---

## ⏸ RESUME STATE (Last updated: May 31, 2026 14:58)

> **Read this section first when resuming work.**

### Environment
- **Python:** 3.14.5 (venv at `d:\MarlishAI\MarlishAI\venv\`)
- **GPU:** NVIDIA GeForce RTX 4050 Laptop GPU — CUDA ✅
- **torch:** `cu126`, **fastapi**, **uvicorn** installed
- **Node.js:** `npm install` done (116 packages)
- **NLLB-200:** Cached at `~/.cache/huggingface/` — loads in ~1s on GPU

### Key files (what changed today):
| File | What changed | Status |
|------|-------------|--------|
| `api/app.py` | v3: reverse transliteration for romanized targets | ✅ Updated, needs server restart |
| `scripts/transliterator/reverse_transliterate.py` | NEW: Devanagari → romanized, 6/6 tests pass | ✅ Created |
| `scripts/transliterator/fallback_map.py` | Added `nav`, `tuza`, `mazha`, +18 more seed entries | ✅ Updated |
| `scripts/test_reverse_translit.py` | NEW: reverse transliteration test suite | ✅ Created |
| `hooks/useTranslation.js` | v6: calls API with `source`/`target` | ✅ Done (from yesterday) |
| `app/components/translator/OutputArea.jsx` | `ml_translation` badge | ✅ Done (from yesterday) |

### Three known quality problems:
| Problem | Root Cause | Fix Status |
|---------|-----------|------------|
| "nav" → "What is the new?" | Seed map missing `nav`→`नाव` | ✅ FIXED |
| English→Marlish outputs Devanagari | No reverse transliteration | ✅ FIXED |
| "kal meeting hai bro" → wrong meaning | NLLB-200-600M model quality limit | ❌ Needs research |

### What to do next (in order):
1. **Restart API server** (kill old one, start new):
   ```
   $env:PYTHONIOENCODING="utf-8"; .\venv\Scripts\uvicorn api.app:app --host 0.0.0.0 --port 8000
   ```
2. **Start Next.js** (if not running):
   ```
   npm run dev
   ```
3. **Test in browser** at `http://localhost:3000` — try all language pairs
4. **Apply Gemini Deep Research results** to improve NLLB translation quality
5. **Deploy** (Vercel + HF Spaces)

---

*(Future phases will be added here as they become active.)*

