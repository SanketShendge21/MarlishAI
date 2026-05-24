"""
Phase 1 — Benchmark Pre-Trained Models & Measure Transliteration Tax

Purpose:
  1. Transliterate Marlish (romanized Marathi) → Devanagari using indic-transliteration
  2. Feed Devanagari into Helsinki-NLP/opus-mt-mr-en
  3. Measure translation quality via BLEU against expected English
  4. Also measure a "quality ceiling" — feeding real Devanagari directly to see
     how much accuracy the transliteration step costs us.

Usage:
  python scripts/test_pretrained_models.py
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from sacrebleu.metrics import BLEU
import torch
import time

# ─────────────────────────────────────────────────────────
# Auto-detect GPU (RTX 3060 or similar CUDA device)
# ─────────────────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[Device] Using: {DEVICE}")
if DEVICE == "cuda":
    print(f"[Device] GPU: {torch.cuda.get_device_name(0)}")

# ─────────────────────────────────────────────────────────
# Test sentences: (marlish_input, gold_devanagari, expected_english)
# gold_devanagari lets us measure the transliteration tax separately
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


def transliterate_to_devanagari(text: str) -> str:
    """
    Baseline transliterator using indic-transliteration (ITRANS → Devanagari).
    Phase 2 will replace this with the proper IndicXlit + fallback pipeline.
    English loanwords will be incorrectly transliterated — that's expected;
    measuring this gap is the whole point of Phase 1.
    """
    tokens = text.split()
    result = []
    for token in tokens:
        try:
            deva = transliterate(token, sanscript.ITRANS, sanscript.DEVANAGARI)
            result.append(deva)
        except Exception:
            result.append(token)  # passthrough on failure
    return " ".join(result)


def test_model(model_name: str, sentences: list):
    """
    Runs two tests:
      A) Transliterated path:  Marlish → baseline transliterate → model → English
      B) Gold Devanagari path: Gold Devanagari → model → English (quality ceiling)
    """
    print(f"\n{'='*70}")
    print(f"  MODEL: {model_name}")
    print(f"{'='*70}")

    print(f"\nLoading model and tokenizer...")
    start_load = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(DEVICE)
    load_time = time.time() - start_load
    print(f"Model loaded in {load_time:.1f}s on {DEVICE}")

    transliterated_translations = []
    gold_translations = []
    references = []

    print(f"\n{'-'*70}")
    print(f"  TEST A: Marlish → Transliterate → Translate (End-to-End)")
    print(f"{'-'*70}")

    for marlish, gold_deva, expected in sentences:
        # Path A: Marlish → baseline transliteration → model
        baseline_deva = transliterate_to_devanagari(marlish)
        inputs_a = tokenizer(baseline_deva, return_tensors="pt", padding=True)
        inputs_a = {k: v.to(DEVICE) for k, v in inputs_a.items()}
        start_t = time.time()
        outputs_a = model.generate(**inputs_a, max_new_tokens=64)
        latency = (time.time() - start_t) * 1000
        translation_a = tokenizer.decode(outputs_a[0], skip_special_tokens=True)

        transliterated_translations.append(translation_a)
        references.append(expected)

        print(f"\n  Marlish:          {marlish}")
        print(f"  Baseline Deva:    {baseline_deva}")
        print(f"  Gold Devanagari:  {gold_deva}")
        print(f"  Translation:      {translation_a}")
        print(f"  Expected:         {expected}")
        print(f"  Latency:          {latency:.0f}ms")

    print(f"\n{'-'*70}")
    print(f"  TEST B: Gold Devanagari → Translate (Quality Ceiling)")
    print(f"{'-'*70}")

    for marlish, gold_deva, expected in sentences:
        # Path B: Gold Devanagari → model (skip transliteration)
        inputs_b = tokenizer(gold_deva, return_tensors="pt", padding=True)
        inputs_b = {k: v.to(DEVICE) for k, v in inputs_b.items()}
        outputs_b = model.generate(**inputs_b, max_new_tokens=64)
        translation_b = tokenizer.decode(outputs_b[0], skip_special_tokens=True)

        gold_translations.append(translation_b)

        print(f"\n  Gold Devanagari:  {gold_deva}")
        print(f"  Translation:      {translation_b}")
        print(f"  Expected:         {expected}")

    # ── BLEU Scoring ──
    bleu = BLEU()

    # references must be a list of lists (one list of refs per hypothesis)
    refs_for_bleu = [[r] for r in references]

    score_e2e = bleu.corpus_score(transliterated_translations, [[r for r in references]])
    score_ceiling = bleu.corpus_score(gold_translations, [[r for r in references]])

    print(f"\n{'='*70}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"  End-to-End BLEU (Marlish → Transliterate → English):  {score_e2e.score:.2f}")
    print(f"  Quality Ceiling BLEU (Gold Devanagari → English):     {score_ceiling.score:.2f}")
    print(f"  Transliteration Tax (ceiling - e2e):                  {score_ceiling.score - score_e2e.score:.2f}")
    print(f"  Model load time:                                      {load_time:.1f}s")
    print(f"{'='*70}")

    return {
        "e2e_bleu": score_e2e.score,
        "ceiling_bleu": score_ceiling.score,
        "tax": score_ceiling.score - score_e2e.score,
        "load_time": load_time,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("  MARLISH.AI — Phase 1: Pre-Trained Model Benchmark")
    print("  Testing: Helsinki-NLP/opus-mt-mr-en")
    print("=" * 70)

    results = test_model("Helsinki-NLP/opus-mt-mr-en", TEST_SENTENCES)

    print(f"\n\n{'='*70}")
    print("  DECISION GUIDE")
    print(f"{'='*70}")
    if results["ceiling_bleu"] > 15:
        print("  ✅ opus-mt produces usable translations from Devanagari input.")
        print("  → Proceed with opus-mt as the production model.")
    else:
        print("  ⚠️  opus-mt quality is low even with gold Devanagari.")
        print("  → Investigate IndicTrans2 API as an alternative.")

    if results["tax"] > 10:
        print(f"  ⚠️  Transliteration tax is HIGH ({results['tax']:.1f} BLEU points).")
        print("  → Phase 2 transliteration pipeline is critical for quality.")
    else:
        print(f"  ✅ Transliteration tax is manageable ({results['tax']:.1f} BLEU points).")

    print(f"{'='*70}")
