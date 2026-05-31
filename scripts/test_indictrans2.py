"""
Phase 1b — Benchmark IndicTrans2 vs opus-mt with our improved transliteration pipeline
======================================================================================

Purpose:
  1. Test IndicTrans2 (ai4bharat/indictrans2-indic-en-dist-200M) on the same
     benchmark sentences from Phase 1
  2. Use our Phase 2 transliteration pipeline (not the broken ITRANS baseline)
  3. Compare quality with opus-mt results from Phase 1
  4. Measure BLEU scores for both transliterated and gold Devanagari paths

Usage:
  python scripts/test_indictrans2.py
"""

import sys
import os
import time
import torch

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sacrebleu.metrics import BLEU

# ─────────────────────────────────────────────────────────
# Auto-detect GPU
# ─────────────────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[Device] Using: {DEVICE}")
if DEVICE == "cuda":
    print(f"[Device] GPU: {torch.cuda.get_device_name(0)}")
    print(f"[Device] VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")

# ─────────────────────────────────────────────────────────
# Test sentences: (marlish_input, gold_devanagari, expected_english)
# Same sentences from Phase 1 for direct comparison
# ─────────────────────────────────────────────────────────
TEST_SENTENCES = [
    ("udya kay scene ahe",       "उद्या काय scene आहे",    "What's the plan for tomorrow?"),
    ("ghar ye bhai",             "घरी ये भाई",              "Come home, bro."),
    ("mi college la jato ahe",   "मी college ला जातो आहे",  "I am going to college."),
    ("kadhi bhetel re tu",       "कधी भेटेल रे तू",         "When will you meet?"),
    ("jevla ka nahi",            "जेवलास का नाही",          "Did you eat or not?"),
    ("kasa ahes mitra",          "कसा आहेस मित्रा",         "How are you, friend?"),
    ("khup busy aahe mi aata",   "खूप busy आहे मी आता",    "I am very busy right now."),
    ("party ahe kal ratra",      "party आहे काल रात्री",    "There is a party tomorrow night."),
    ("mala mahit nahi",          "मला माहित नाही",           "I don't know."),
    ("tu kuthe ahes",            "तू कुठे आहेस",            "Where are you?"),
]


def test_indictrans2():
    """Test IndicTrans2 with our improved transliteration pipeline."""

    # ── Load our transliteration pipeline ──
    print("\n[1/3] Loading Marlish Transliteration Pipeline...")
    from scripts.transliterator.pipeline import MarlishTransliterationPipeline
    translit = MarlishTransliterationPipeline()
    print("  ✅ Pipeline loaded.\n")

    # ── Load IndicTransToolkit processor ──
    print("[2/3] Loading IndicProcessor (local pure-Python port)...")
    try:
        from scripts.indic_processor import IndicProcessor
        ip = IndicProcessor(inference=True)
        print("  ✅ IndicProcessor loaded.\n")
    except ImportError as e:
        print(f"  ❌ IndicProcessor failed to load: {e}")
        print("  Run: pip install sacremoses indic-nlp-library-itt")
        return None

    # ── Load IndicTrans2 model ──
    model_name = "ai4bharat/indictrans2-indic-en-dist-200M"
    src_lang = "mar_Deva"  # Marathi Devanagari
    tgt_lang = "eng_Latn"  # English Latin

    print(f"[3/3] Loading model: {model_name}")
    start_load = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    # Use float16 on GPU, float32 on CPU
    dtype = torch.float16 if DEVICE == "cuda" else torch.float32
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=dtype,
    ).to(DEVICE)
    load_time = time.time() - start_load
    print(f"  ✅ Model loaded in {load_time:.1f}s on {DEVICE}\n")

    # ── Test A: Marlish → Our Pipeline → IndicTrans2 ──
    print("=" * 70)
    print("  TEST A: Marlish → Transliteration Pipeline → IndicTrans2")
    print("=" * 70)

    translit_translations = []
    references = []

    for marlish, gold_deva, expected in TEST_SENTENCES:
        # Step 1: Transliterate with our pipeline
        our_deva = translit.transliterate(marlish)

        # Step 2: Preprocess for IndicTrans2
        batch = ip.preprocess_batch([our_deva], src_lang=src_lang, tgt_lang=tgt_lang)
        inputs = tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(DEVICE)

        # Step 3: Generate translation
        start_t = time.time()
        with torch.no_grad():
            generated = model.generate(**inputs, num_beams=5, max_new_tokens=128)
        latency = (time.time() - start_t) * 1000

        # Step 4: Decode and postprocess
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translation = ip.postprocess_batch(decoded, lang=tgt_lang)[0]

        translit_translations.append(translation)
        references.append(expected)

        print(f"\n  Marlish:          {marlish}")
        print(f"  Our Devanagari:   {our_deva}")
        print(f"  Gold Devanagari:  {gold_deva}")
        print(f"  Translation:      {translation}")
        print(f"  Expected:         {expected}")
        print(f"  Latency:          {latency:.0f}ms")

    # ── Test B: Gold Devanagari → IndicTrans2 (Quality Ceiling) ──
    print(f"\n{'=' * 70}")
    print("  TEST B: Gold Devanagari → IndicTrans2 (Quality Ceiling)")
    print("=" * 70)

    gold_translations = []

    for marlish, gold_deva, expected in TEST_SENTENCES:
        batch = ip.preprocess_batch([gold_deva], src_lang=src_lang, tgt_lang=tgt_lang)
        inputs = tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(DEVICE)

        with torch.no_grad():
            generated = model.generate(**inputs, num_beams=5, max_new_tokens=128)

        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translation = ip.postprocess_batch(decoded, lang=tgt_lang)[0]

        gold_translations.append(translation)

        print(f"\n  Gold Devanagari:  {gold_deva}")
        print(f"  Translation:      {translation}")
        print(f"  Expected:         {expected}")

    # ── BLEU Scoring ──
    bleu = BLEU()

    score_e2e = bleu.corpus_score(translit_translations, [[r for r in references]])
    score_ceiling = bleu.corpus_score(gold_translations, [[r for r in references]])

    print(f"\n{'=' * 70}")
    print("  RESULTS SUMMARY — IndicTrans2")
    print(f"{'=' * 70}")
    print(f"  End-to-End BLEU (Marlish → Our Pipeline → IndicTrans2):  {score_e2e.score:.2f}")
    print(f"  Quality Ceiling BLEU (Gold Devanagari → IndicTrans2):    {score_ceiling.score:.2f}")
    print(f"  Transliteration Tax (ceiling - e2e):                     {score_ceiling.score - score_e2e.score:.2f}")
    print(f"  Model load time:                                         {load_time:.1f}s")
    print(f"\n  COMPARISON WITH PHASE 1 (opus-mt):")
    print(f"  opus-mt End-to-End BLEU:      0.45")
    print(f"  opus-mt Quality Ceiling BLEU: 8.37")
    print(f"  IndicTrans2 End-to-End BLEU:  {score_e2e.score:.2f}")
    print(f"  IndicTrans2 Ceiling BLEU:     {score_ceiling.score:.2f}")
    print(f"{'=' * 70}")

    return {
        "e2e_bleu": score_e2e.score,
        "ceiling_bleu": score_ceiling.score,
        "tax": score_ceiling.score - score_e2e.score,
        "load_time": load_time,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("  MARLISH.AI — Phase 1b: IndicTrans2 Benchmark")
    print("  Using Phase 2 Transliteration Pipeline (100% accuracy)")
    print("=" * 70)

    results = test_indictrans2()

    if results:
        print(f"\n{'=' * 70}")
        print("  DECISION")
        print(f"{'=' * 70}")
        if results["ceiling_bleu"] > 15:
            print("  ✅ IndicTrans2 produces usable translations!")
            print("  → Use IndicTrans2 for API path (Phase 4)")
            if results["e2e_bleu"] > 10:
                print("  ✅ End-to-end pipeline produces usable output!")
                print("  → Full pipeline is viable for production")
        else:
            print("  ⚠️  IndicTrans2 quality is still low.")
            print("  → Further investigation needed.")
        print(f"{'=' * 70}")
