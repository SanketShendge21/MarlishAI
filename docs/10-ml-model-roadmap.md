# Marlish.AI — ML Model Roadmap

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Current

---

## Model Evolution Timeline

```
Apr 2026    mt5-small fine-tuning          → BLEU ~3, abandoned
    ↓
May 2026    IndicTrans2 (AI4Bharat)        → Good quality, fairseq incompatible
    ↓
May 2026    NLLB-200-600M                  → Works, baseline established
    ↓
Jun 2026    NLLB-200-1.3B                  → Better quality, same speed on GPU
    ↓
Jun 2026    + Gemini GEC                   → English output polished
    ↓
Jun 2026    + Transliteration fixes        → Marlish/Hinglish 6/13 → 11/13
    ↓
Current     Production-ready v1.0          → 10-13/13 across all directions
```

## Current Production Stack

### NLLB-200-1.3B
- **Role:** Core translation model
- **Why:** Best quality-to-size ratio for Indic languages that runs on consumer hardware
- **Languages used:** `eng_Latn`, `mar_Deva`, `hin_Deva`
- **Inference:** ~1-2s (GPU) / ~15-30s (CPU)

### Gemini 2.5-flash-lite
- **Role:** Grammar Error Correction (English output only)
- **Why:** Free tier, fast, improves fluency without changing meaning
- **Trigger:** Only when API key is set and target is English
- **Fallback:** Raw NLLB output (still usable)

### Custom Transliteration Pipeline
- **Role:** Romanized text → Devanagari (preprocessing for NLLB)
- **Tiers:**
  1. IndicXlit (planned — AI-powered, highest accuracy)
  2. Seed Map (active — 400+ words, O(1) lookup)
  3. Phoneme Rules (active — character-level with conjunct support)

## Future Model Upgrades

| Model | Purpose | When | Effort |
|-------|---------|------|--------|
| **QLoRA fine-tune** | Improve NLLB on Marlish-specific patterns | Post-launch | High |
| **IndicXlit** | Tier 1 transliteration (replaces phoneme rules for unknown words) | Post-launch | Medium |
| **NLLB-200-3.3B** | Better quality (needs 8GB+ VRAM) | When GPU budget available | Low |
| **Whisper** | Speech-to-text input | Phase 3 | Medium |
| **IndicTTS** | Text-to-speech output | Phase 3 | Medium |

## Models Evaluated & Rejected

| Model | Reason for Rejection |
|-------|---------------------|
| `google/mt5-small` | BLEU ~3 after fine-tuning on noisy dataset |
| IndicTrans2 | fairseq dependency broken on Windows/Python 3.14 |
| `opus-mt` (Helsinki-NLP) | No Marathi language support |
| `nllb-200-distilled-600M` | Works but 1.3B is noticeably better quality |
| Custom LSTM/Transformer | Insufficient training data, months of work |
| GPT-4o / Claude API | Too expensive for real-time per-request usage |
