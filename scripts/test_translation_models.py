"""
Phase 3 — Benchmark Translation Models for Marlish Pipeline
============================================================

Tests multiple translation models (Marathi Devanagari → English) using our
Phase 2 transliteration pipeline. Compares against Phase 1 opus-mt results.

Models tested:
  1. facebook/nllb-200-distilled-600M (open, no login needed)
  2. ai4bharat/indictrans2-indic-en-dist-200M (gated, needs HF login)

Usage:
  python scripts/test_translation_models.py
  python scripts/test_translation_models.py --model nllb
  python scripts/test_translation_models.py --model indictrans2
"""

import sys
import os
import time
import argparse

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sacrebleu.metrics import BLEU

# ─────────────────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[Device] Using: {DEVICE}")
if DEVICE == "cuda":
    print(f"[Device] GPU: {torch.cuda.get_device_name(0)}")

# ─────────────────────────────────────────────────────────
# Same test sentences from Phase 1 for direct comparison
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


# ─────────────────────────────────────────────────────────
# Model configs
# ─────────────────────────────────────────────────────────
MODEL_CONFIGS = {
    "nllb": {
        "name": "facebook/nllb-200-distilled-600M",
        "src_lang": "mar_Deva",
        "tgt_lang": "eng_Latn",
        "type": "nllb",
    },
    "indictrans2": {
        "name": "ai4bharat/indictrans2-indic-en-dist-200M",
        "src_lang": "mar_Deva",
        "tgt_lang": "eng_Latn",
        "type": "indictrans2",
    },
}


def translate_nllb(model, tokenizer, text, src_lang, tgt_lang):
    """Translate using NLLB-200 model."""
    tokenizer.src_lang = src_lang
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(DEVICE)

    # Get target language token id for forced_bos
    tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang)

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            forced_bos_token_id=tgt_lang_id,
            max_new_tokens=128,
        )

    return tokenizer.decode(generated[0], skip_special_tokens=True)


def translate_indictrans2(model, tokenizer, ip, text, src_lang, tgt_lang):
    """Translate using IndicTrans2 with IndicProcessor preprocessing."""
    # Preprocess
    batch = ip.preprocess_batch([text], src_lang=src_lang, tgt_lang=tgt_lang)
    inputs = tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        generated = model.generate(**inputs, num_beams=5, max_new_tokens=128)

    decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
    translations = ip.postprocess_batch(decoded, lang=tgt_lang)
    return translations[0]


def run_benchmark(model_key):
    """Run benchmark for a specific model."""
    config = MODEL_CONFIGS[model_key]
    model_name = config["name"]
    model_type = config["type"]

    # ── Load transliteration pipeline ──
    print("\n[1/3] Loading Marlish Transliteration Pipeline...")
    from scripts.transliterator.pipeline import MarlishTransliterationPipeline
    translit = MarlishTransliterationPipeline()
    print("  ✅ Pipeline loaded.\n")

    # ── Load IndicProcessor for IndicTrans2 ──
    ip = None
    if model_type == "indictrans2":
        print("[2/3] Loading IndicProcessor...")
        try:
            from scripts.indic_processor import IndicProcessor
            ip = IndicProcessor(inference=True)
            print("  ✅ IndicProcessor loaded.\n")
        except ImportError as e:
            print(f"  ❌ IndicProcessor failed: {e}")
            return None
    else:
        print("[2/3] IndicProcessor not needed for NLLB.\n")

    # ── Load model ──
    print(f"[3/3] Loading model: {model_name}")
    start_load = time.time()
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        dtype = torch.float16 if DEVICE == "cuda" else torch.float32
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=dtype,
        ).to(DEVICE)
    except OSError as e:
        if "gated" in str(e).lower() or "401" in str(e):
            print(f"\n  ❌ Model is GATED. You need to:")
            print(f"     1. Go to https://huggingface.co/{model_name}")
            print(f"     2. Accept the license terms")
            print(f"     3. Run: huggingface-cli login")
            return None
        raise
    load_time = time.time() - start_load
    print(f"  ✅ Model loaded in {load_time:.1f}s on {DEVICE}\n")

    # ── Test A: Marlish → Our Pipeline → Model ──
    print("=" * 70)
    print(f"  TEST A: Marlish → Pipeline → {model_key.upper()}")
    print("=" * 70)

    translit_translations = []
    references = []

    for marlish, gold_deva, expected in TEST_SENTENCES:
        our_deva = translit.transliterate(marlish)

        start_t = time.time()
        if model_type == "nllb":
            translation = translate_nllb(
                model, tokenizer, our_deva,
                config["src_lang"], config["tgt_lang"]
            )
        else:
            translation = translate_indictrans2(
                model, tokenizer, ip, our_deva,
                config["src_lang"], config["tgt_lang"]
            )
        latency = (time.time() - start_t) * 1000

        translit_translations.append(translation)
        references.append(expected)

        print(f"\n  Marlish:          {marlish}")
        print(f"  Our Devanagari:   {our_deva}")
        print(f"  Translation:      {translation}")
        print(f"  Expected:         {expected}")
        print(f"  Latency:          {latency:.0f}ms")

    # ── Test B: Gold Devanagari → Model (Quality Ceiling) ──
    print(f"\n{'=' * 70}")
    print(f"  TEST B: Gold Devanagari → {model_key.upper()} (Quality Ceiling)")
    print("=" * 70)

    gold_translations = []

    for marlish, gold_deva, expected in TEST_SENTENCES:
        if model_type == "nllb":
            translation = translate_nllb(
                model, tokenizer, gold_deva,
                config["src_lang"], config["tgt_lang"]
            )
        else:
            translation = translate_indictrans2(
                model, tokenizer, ip, gold_deva,
                config["src_lang"], config["tgt_lang"]
            )

        gold_translations.append(translation)

        print(f"\n  Gold Devanagari:  {gold_deva}")
        print(f"  Translation:      {translation}")
        print(f"  Expected:         {expected}")

    # ── BLEU Scoring ──
    bleu = BLEU()
    score_e2e = bleu.corpus_score(translit_translations, [[r for r in references]])
    score_ceiling = bleu.corpus_score(gold_translations, [[r for r in references]])

    print(f"\n{'=' * 70}")
    print(f"  RESULTS SUMMARY — {model_key.upper()}")
    print(f"{'=' * 70}")
    print(f"  End-to-End BLEU (Marlish → Pipeline → {model_key}):  {score_e2e.score:.2f}")
    print(f"  Quality Ceiling BLEU (Gold Deva → {model_key}):      {score_ceiling.score:.2f}")
    print(f"  Transliteration Tax:                                  {score_ceiling.score - score_e2e.score:.2f}")
    print(f"  Model load time:                                      {load_time:.1f}s")
    print(f"\n  COMPARISON WITH PHASE 1 (opus-mt):")
    print(f"  opus-mt End-to-End BLEU:      0.45")
    print(f"  opus-mt Quality Ceiling BLEU: 8.37")
    print(f"  {model_key} End-to-End BLEU:  {score_e2e.score:.2f}")
    print(f"  {model_key} Ceiling BLEU:     {score_ceiling.score:.2f}")
    print(f"{'=' * 70}")

    return {
        "model": model_key,
        "e2e_bleu": score_e2e.score,
        "ceiling_bleu": score_ceiling.score,
        "tax": score_ceiling.score - score_e2e.score,
        "load_time": load_time,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark translation models")
    parser.add_argument(
        "--model", choices=["nllb", "indictrans2", "all"], default="nllb",
        help="Which model to test (default: nllb)"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  MARLISH.AI — Phase 3: Translation Model Benchmark")
    print("  Using Phase 2 Transliteration Pipeline (100% accuracy)")
    print("=" * 70)

    models_to_test = ["nllb", "indictrans2"] if args.model == "all" else [args.model]
    all_results = {}

    for model_key in models_to_test:
        results = run_benchmark(model_key)
        if results:
            all_results[model_key] = results

    if all_results:
        print(f"\n\n{'=' * 70}")
        print("  FINAL COMPARISON")
        print(f"{'=' * 70}")
        print(f"  {'Model':<20} {'E2E BLEU':>10} {'Ceiling BLEU':>14} {'Tax':>8}")
        print(f"  {'-'*52}")
        print(f"  {'opus-mt (Phase 1)':<20} {'0.45':>10} {'8.37':>14} {'7.91':>8}")
        for key, r in all_results.items():
            print(f"  {key:<20} {r['e2e_bleu']:>10.2f} {r['ceiling_bleu']:>14.2f} {r['tax']:>8.2f}")
        print(f"{'=' * 70}")
