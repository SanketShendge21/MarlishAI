"""
Phoneme-to-Grapheme Rules for Marlish Transliteration

Last-resort character-level mapping for tokens NOT found in the frequency map.
Converts romanized Marathi phonemes to Devanagari graphemes using ordered
substitution rules. Longer sequences are matched first to avoid partial matches.

These rules handle the common romanization patterns used in Indian texting:
  - "kh" → ख  (not क + ह)
  - "aa" → आ  (long vowel)
  - "sh" → श  (single consonant)
"""

# ─────────────────────────────────────────────────────────
# Phoneme rules — ORDERED from longest to shortest match
# This ordering is critical: "dh" must match before "d"
# ─────────────────────────────────────────────────────────
PHONEME_RULES = [
    # ── Conjuncts & special combinations (3+ chars) ──
    ("shri", "श्री"),
    ("tra", "त्र"),
    ("dny", "ज्ञ"),
    ("gya", "ज्ञ"),
    ("ksh", "क्ष"),
    ("shr", "श्र"),

    # ── Aspirated consonants (2-3 chars) ──
    ("chh", "छ"),   # must be before "ch"
    ("kh", "ख"),
    ("gh", "घ"),
    ("ch", "च"),
    ("jh", "झ"),
    ("th", "थ"),    # dental aspirated
    ("dh", "ध"),    # dental aspirated
    ("ph", "फ"),
    ("bh", "भ"),
    ("sh", "श"),

    # ── Retroflex consonants ──
    ("tt", "ट"),
    ("dd", "ड"),
    ("nn", "ण"),

    # ── Long vowels (2 chars) ──
    ("aa", "आ"),
    ("ii", "ई"),
    ("ee", "ई"),
    ("oo", "ऊ"),
    ("uu", "ऊ"),
    ("ai", "ऐ"),
    ("ei", "ऐ"),
    ("au", "औ"),
    ("ou", "औ"),

    # ── Nasals & special ──
    ("ng", "ं"),
    ("ny", "ञ"),

    # ── Single consonants ──
    ("k", "क"),
    ("g", "ग"),
    ("c", "क"),    # 'c' as in 'cat' → क
    ("j", "ज"),
    ("t", "त"),
    ("d", "द"),
    ("n", "न"),
    ("p", "प"),
    ("b", "ब"),
    ("m", "म"),
    ("y", "य"),
    ("r", "र"),
    ("l", "ल"),
    ("v", "व"),
    ("w", "व"),
    ("s", "स"),
    ("h", "ह"),
    ("f", "फ"),    # borrowed sound
    ("z", "ज़"),    # borrowed sound
    ("x", "क्स"),

    # ── Short vowels ──
    ("a", "अ"),
    ("i", "इ"),
    ("e", "ए"),
    ("o", "ओ"),
    ("u", "उ"),
]


def apply_phoneme_rules(token: str) -> str:
    """
    Convert a romanized token to Devanagari using character-level phoneme rules.

    This is the LAST RESORT transliterator — used only when:
      1. IndicXlit is unavailable or fails
      2. The token is not in the frequency map

    The result won't be perfect for all words, but provides a reasonable
    best-guess that the translation model can often still work with.

    Args:
        token: Romanized Marlish/Marathi word (lowercase expected)

    Returns:
        Devanagari string (best-effort transliteration)
    """
    token = token.lower().strip()
    result = []
    i = 0

    while i < len(token):
        matched = False
        # Try longest matches first (3 chars, then 2, then 1)
        for length in (3, 2, 1):
            chunk = token[i:i + length]
            for roman, deva in PHONEME_RULES:
                if chunk == roman[:length] and token[i:i + len(roman)] == roman:
                    result.append(deva)
                    i += len(roman)
                    matched = True
                    break
            if matched:
                break

        if not matched:
            # Unknown character — pass through as-is
            result.append(token[i])
            i += 1

    return "".join(result)


# ─────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_words = [
        "udya", "kay", "ahe", "aahe", "mitra",
        "kasa", "ghar", "khup", "nahi", "bhetel",
        "jevla", "ratra", "jato", "mahit", "kuthe",
    ]
    print("Phoneme Rule Transliteration Test:")
    print("-" * 40)
    for word in test_words:
        deva = apply_phoneme_rules(word)
        print(f"  {word:15s} → {deva}")
