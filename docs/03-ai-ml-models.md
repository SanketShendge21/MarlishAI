# Marlish.AI — AI/ML Models & NLP Strategy

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Production

---

## 1. Model Stack

### 1.1 Primary: NLLB-200-1.3B (Meta)
- **Purpose:** Neural machine translation between all supported language pairs
- **Hugging Face:** `facebook/nllb-200-1.3B`
- **Parameters:** 1.3 billion (Seq2Seq, encoder-decoder)
- **Languages:** 200 (using `eng_Latn`, `mar_Deva`, `hin_Deva`)
- **BLEU scores:** Competitive with commercial translators for Indic languages
- **VRAM:** ~3GB (GPU) or ~5GB RAM (CPU)
- **Why this model:**
  - Free, open-source (CC-BY-NC-4.0)
  - Supports both Marathi and Hindi natively
  - No fine-tuning needed — works out of the box
  - 1.3B is the sweet spot: better quality than 600M, runs on consumer GPU

### 1.2 Secondary: Gemini 2.5-flash-lite (Google)
- **Purpose:** Grammar Error Correction (GEC) — polishes English output
- **SDK:** `google-genai` Python package
- **Cost:** Free tier (15 RPM, 1M tokens/day)
- **When used:** Only for English target translations
- **Fallback:** If Gemini fails or no API key, raw NLLB output is returned
- **Impact:** Fixes awkward phrasing, adds natural fluency

## 2. Transliteration Pipeline (Custom)

Not a model, but a critical preprocessing step. Converts romanized chat text to proper Devanagari that NLLB can understand.

### Tier 1: IndicXlit (AI-powered, not yet active)
- **Source:** AI4Bharat
- **Status:** Planned post-launch (requires fairseq, complex Windows install)
- **Accuracy:** Highest

### Tier 2: Seed Map (Active — 400+ words)
- **Type:** Dictionary lookup, O(1)
- **Coverage:** Common Marathi words, Hindi words, food items, chat loanwords, travel/formal vocabulary
- **File:** `scripts/transliterator/fallback_map.py`

### Tier 3: Phoneme Rules (Active — fallback)
- **Type:** Rule-based character-level conversion
- **Features:** Consonant clusters (halant), long vowels, matra logic
- **File:** `scripts/transliterator/phoneme_rules.py`
- **Limitation:** Cannot distinguish short/long 'a' — seed map covers known words

### Reverse Transliteration (Devanagari → romanized)
- **Purpose:** For Marlish/Hinglish output targets
- **Features:** Word-level lookup (inverse seed map) → character-level fallback
- **Post-processing:** Devanagari digit conversion (१→1), simplified endings
- **File:** `scripts/transliterator/reverse_transliterate.py`

## 3. Models Evaluated & Rejected

| Model | Why Rejected |
|-------|-------------|
| `google/mt5-small` | Fine-tuned on noisy data, BLEU ~3. Too weak for production. |
| IndicTrans2 (AI4Bharat) | Good quality but complex dependency (fairseq), Windows incompatible |
| `opus-mt` (Helsinki-NLP) | No Marathi support |
| `nllb-200-distilled-600M` | Works but 1.3B is noticeably better, same speed on GPU |
| Custom LSTM/Transformer | Not enough training data, would take months |

## 4. Quality Metrics

### Carnival Tours Test (104 segments, 8 directions, June 2026)
| Direction | Score | Notes |
|-----------|-------|-------|
| Hindi → English | 12/13 | Best performer |
| English → Hindi | 13/13 | Excellent |
| Marathi → English | 11/13 | Strong |
| English → Marathi | 12/13 | Strong |
| Marlish → English | 11/13 | Good (after translit fixes) |
| Hinglish → English | 11/13 | Good (after translit fixes) |
| English → Marlish | 10/13 | Usable (reverse translit artifacts) |
| English → Hinglish | 10/13 | Usable (reverse translit artifacts) |

### Scoring Criteria
- ✅ Correct: Meaning is preserved, even if wording differs from expected
- ⚠️ Close: Meaning is mostly correct, minor details lost
- ❌ Wrong: Meaning is incorrect or nonsensical
