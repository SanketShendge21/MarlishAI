"""
Marlish Transliteration Pipeline — Accuracy Evaluation
=======================================================
Tests the pipeline against 55+ real Marlish sentences with
gold-standard Devanagari references.

Metrics reported:
  - Per-token accuracy (correct Devanagari tokens / total transliterated tokens)
  - Per-sentence exact match rate
  - Tier breakdown (fallback_map vs phoneme_rules)
  - Per-sentence error listing for debugging

Usage:
    python scripts/evaluate_transliteration.py
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.transliterator.pipeline import MarlishTransliterationPipeline


# ─────────────────────────────────────────────────────────
# Gold-standard test set: (marlish_input, expected_devanagari_output)
#
# Rules for expected output:
#   - English loanwords stay as-is (scene, party, bro, college, etc.)
#   - Numbers stay as-is
#   - Devanagari in input stays as-is
#   - Only romanized Marlish tokens get transliterated
# ─────────────────────────────────────────────────────────
TEST_SET = [
    # ── Greetings & basics ──
    ("kasa ahes mitra", "कसा आहेस मित्र"),
    ("mi bara ahe", "मी बरा आहे"),
    ("tu kuthe ahes", "तू कुठे आहेस"),
    ("kay challay", "काय चाल्लय"),
    ("kay mhantos", "काय म्हणतोस"),

    # ── Daily conversation ──
    ("udya kay scene ahe bro", "उद्या काय scene आहे bro"),
    ("mi college la jato ahe", "मी college ला जातो आहे"),
    ("ghar ye bhai", "घर ये भाई"),
    ("mala mahit nahi", "मला माहित नाही"),
    ("khup busy aahe mi aata", "खूप busy आहे मी आता"),

    # ── Questions ──
    ("kadhi bhetel re tu", "कधी भेटेल रे तू"),
    ("jevla ka nahi", "जेवला का नाही"),
    ("party ahe kal ratra", "party आहे काल रात्र"),
    ("kuthe ahes tu aata", "कुठे आहेस तू आता"),
    ("kiti vajle", "किती वाजले"),

    # ── Emotions & reactions ──
    ("khup chhan", "खूप छान"),
    ("mast ahe ekdum", "मस्त आहे एकदम"),
    ("vaait vatla mala", "वाईट वाटला मला"),
    ("khup haslo mi", "खूप हसलो मी"),
    ("ekdum boring hota", "एकदम boring होता"),

    # ── Instructions & requests ──
    ("lavkar ye ghari", "लवकर ये घरी"),
    ("mala call kar", "मला call कर"),
    ("thamb thoda", "थांब थोडा"),
    ("he bagh re", "हे बघ रे"),
    ("mala sang na", "मला सांग ना"),

    # ── Food & daily life ──
    ("aaj jevana kay ahe", "आज जेवण काय आहे"),
    ("paani de mala", "पाणी दे मला"),
    ("mala bhuk lagali", "मला भूक लागली"),
    ("coffee piyaycha ka", "coffee पियायचा का"),
    ("jevan tayar ahe ka", "जेवण तयार आहे का"),

    # ── Family & relationships ──
    ("aai ghari ahe", "आई घरी आहे"),
    ("baba office la gele", "बाबा office ला गेले"),
    ("tai la sang", "ताई ला सांग"),
    ("bhau kuthe ahe", "भाऊ कुठे आहे"),
    ("dost yeto aaj", "दोस्त येतो आज"),

    # ── Planning & scheduling ──
    ("udya movie la jauycha ka", "उद्या movie ला जाऊयचा का"),
    ("kal mi free ahe", "काल मी free आहे"),
    ("sandhyakali bhet", "संध्याकाळी भेट"),
    ("sakali lavkar uth", "सकाळी लवकर उठ"),
    ("ratri ghari ye", "रात्री घरी ये"),

    # ── Work & study ──
    ("kaam khup ahe aaj", "काम खूप आहे आज"),
    ("class la ja", "class ला जा"),
    ("exam nantar bhetuyaa", "exam नंतर भेटूया"),
    ("office madhe ahe mi", "office मध्ये आहे मी"),
    ("meeting la late honar", "meeting ला late होणार"),

    # ── Affirmative / negative ──
    ("ho chalel", "हो चालेल"),
    ("nahi mala nako", "नाही मला नको"),
    ("hoy barobar ahe", "होय बरोबर आहे"),
    ("nai re nai", "नाही रे नाही"),

    # ── Mixed code-switching ──
    ("mi shopping la jato ahe mall la", "मी shopping ला जातो आहे mall ला"),
    ("whatsapp var message kar", "whatsapp वर message कर"),
    ("uber book kar lavkar", "uber book कर लवकर"),
    ("instagram var photo takla", "instagram वर photo टाकला"),
    ("cricket match bagh re", "cricket match बघ रे"),

    # ── Longer conversational sentences ──
    ("mi aaj ghari basun kaam karto", "मी आज घरी बसून काम करतो"),
]

# Total: 55 test sentences


def normalize_for_comparison(text: str) -> list:
    """Split and lowercase for token-level comparison."""
    return text.strip().split()


def evaluate():
    pipeline = MarlishTransliterationPipeline()

    total_tokens = 0
    correct_tokens = 0
    exact_match_count = 0
    errors = []

    print("\n" + "=" * 70)
    print("  Marlish Transliteration Pipeline — Accuracy Evaluation")
    print(f"  Test set: {len(TEST_SET)} sentences")
    print("=" * 70)

    for i, (marlish_input, expected_output) in enumerate(TEST_SET, 1):
        pipeline.reset_stats()
        actual_output = pipeline.transliterate(marlish_input)

        expected_tokens = normalize_for_comparison(expected_output)
        actual_tokens = normalize_for_comparison(actual_output)

        # Pad to equal length for comparison
        max_len = max(len(expected_tokens), len(actual_tokens))
        expected_padded = expected_tokens + ["<MISSING>"] * (max_len - len(expected_tokens))
        actual_padded = actual_tokens + ["<EXTRA>"] * (max_len - len(actual_tokens))

        sentence_correct = True
        sentence_errors = []

        for exp_tok, act_tok in zip(expected_padded, actual_padded):
            total_tokens += 1
            if exp_tok == act_tok:
                correct_tokens += 1
            else:
                sentence_correct = False
                sentence_errors.append((exp_tok, act_tok))

        if sentence_correct:
            exact_match_count += 1
            status = "✅"
        else:
            status = "❌"
            errors.append({
                "index": i,
                "input": marlish_input,
                "expected": expected_output,
                "actual": actual_output,
                "token_errors": sentence_errors,
            })

        print(f"\n  [{i:2d}] {status}")
        print(f"       Input:    {marlish_input}")
        print(f"       Expected: {expected_output}")
        print(f"       Actual:   {actual_output}")
        if sentence_errors:
            for exp, act in sentence_errors:
                print(f"       ⚠ {exp} → got: {act}")

    # ── Summary ──
    token_accuracy = (correct_tokens / total_tokens * 100) if total_tokens else 0
    sentence_accuracy = (exact_match_count / len(TEST_SET) * 100) if TEST_SET else 0

    print("\n" + "=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print(f"  Total sentences:       {len(TEST_SET)}")
    print(f"  Exact match:           {exact_match_count}/{len(TEST_SET)} ({sentence_accuracy:.1f}%)")
    print(f"  Total tokens:          {total_tokens}")
    print(f"  Correct tokens:        {correct_tokens}/{total_tokens} ({token_accuracy:.1f}%)")
    print(f"  Pipeline tier stats:   {pipeline.get_stats()}")

    if errors:
        print(f"\n  ── {len(errors)} SENTENCES WITH ERRORS ──")
        for err in errors:
            print(f"\n  [{err['index']}] {err['input']}")
            for exp, act in err["token_errors"]:
                print(f"       Expected: {exp}  |  Got: {act}")

    print("\n" + "=" * 70)
    print("  Evaluation complete.")
    print("=" * 70)

    return {
        "sentence_accuracy": sentence_accuracy,
        "token_accuracy": token_accuracy,
        "exact_match": exact_match_count,
        "total_sentences": len(TEST_SET),
        "correct_tokens": correct_tokens,
        "total_tokens": total_tokens,
    }


if __name__ == "__main__":
    evaluate()
