"""
Phoneme-to-Grapheme Rules for Marlish Transliteration

Last-resort character-level mapping for tokens NOT found in the frequency map.
Converts romanized Marathi phonemes to Devanagari graphemes using proper
consonant-vowel joining with matra (dependent vowel) and halant (virama) logic.

Key improvement over naive character substitution:
  - "ka"  → "क"   (inherent 'a' handled correctly, not "कअ")
  - "ki"  → "कि"  (consonant + i-matra)
  - "kaa" → "का"   (consonant + aa-matra)
  - "llo" → "ल्लो" (doubled consonant conjunct + o-matra)

Algorithm:
  1. Tokenize romanized input into phoneme tokens (consonant/vowel/unknown)
  2. Render tokens using Devanagari joining rules:
     - Consonant + Vowel → consonant base + vowel matra
     - Consonant + same Consonant → conjunct via halant
     - Consonant + different Consonant → inherent schwa (no halant)
     - Vowel at start or after vowel → independent vowel form
"""

# ─────────────────────────────────────────────────────────
# Consonant phonemes → base Devanagari consonant
# Sorted longest-first within each group for greedy matching
# ─────────────────────────────────────────────────────────
CONSONANT_MAP = {
    # 3-char combinations
    "ksh": "क्ष",
    "chh": "छ",
    "shr": "श्र",

    # 2-char Marathi-specific
    "mh": "म्ह",     # म्हणजे, म्हणून — very common in Marathi

    # 2-char aspirated consonants
    "kh": "ख",
    "gh": "घ",
    "ch": "च",
    "jh": "झ",
    "th": "थ",
    "dh": "ध",
    "ph": "फ",
    "bh": "भ",
    "sh": "श",

    # 2-char retroflex / nasal
    "tt": "ट",
    "dd": "ड",
    "nn": "ण",       # retroflex nasal (Marathi)
    "ng": "ं",       # anusvara
    "ny": "ञ",       # palatal nasal

    # Single consonants
    "k": "क",
    "g": "ग",
    "c": "क",        # 'c' as in 'cat' → क
    "j": "ज",
    "t": "त",
    "d": "द",
    "n": "न",
    "p": "प",
    "b": "ब",
    "m": "म",
    "y": "य",
    "r": "र",
    "l": "ल",
    "v": "व",
    "w": "व",
    "s": "स",
    "h": "ह",
    "f": "फ",        # borrowed sound
    "z": "ज़",       # borrowed sound
    "x": "क्स",
}

# ─────────────────────────────────────────────────────────
# Vowel phonemes → (independent form, matra/dependent form)
# Independent: used at start of word or after another vowel
# Matra: used after a consonant
# ─────────────────────────────────────────────────────────
VOWEL_MAP = {
    # Long vowels (2-char, must match before single-char)
    "aa": ("आ", "ा"),
    "ii": ("ई", "ी"),
    "ee": ("ई", "ी"),
    "oo": ("ऊ", "ू"),
    "uu": ("ऊ", "ू"),
    "ai": ("ऐ", "ै"),
    "ei": ("ऐ", "ै"),
    "au": ("औ", "ौ"),
    "ou": ("औ", "ौ"),

    # Short vowels (1-char)
    "a": ("अ", ""),     # inherent 'a' — no matra needed
    "i": ("इ", "ि"),
    "e": ("ए", "े"),
    "o": ("ओ", "ो"),
    "u": ("उ", "ु"),
}

HALANT = "्"

# Pre-sorted keys for greedy matching (longest first)
_CONSONANT_KEYS = sorted(CONSONANT_MAP.keys(), key=len, reverse=True)
_VOWEL_KEYS = sorted(VOWEL_MAP.keys(), key=len, reverse=True)


def _tokenize(text):
    """
    Tokenize romanized text into classified phoneme tokens.

    Returns:
        List of tuples:
          ("C", roman_key)  — consonant phoneme
          ("V", roman_key)  — vowel phoneme
          ("X", char)       — unknown character (pass-through)
    """
    text = text.lower().strip()
    tokens = []
    i = 0

    while i < len(text):
        best_match = None
        best_type = None
        best_len = 0

        # Try consonant matches (longest first)
        for key in _CONSONANT_KEYS:
            klen = len(key)
            if klen <= best_len:
                break  # can't beat current best
            if text[i:i + klen] == key:
                best_match = key
                best_type = "C"
                best_len = klen
                break  # already longest-first, take it

        # Try vowel matches (longest first)
        for key in _VOWEL_KEYS:
            klen = len(key)
            if klen <= best_len:
                break
            if text[i:i + klen] == key:
                best_match = key
                best_type = "V"
                best_len = klen
                break

        if best_match:
            tokens.append((best_type, best_match))
            i += best_len
        else:
            tokens.append(("X", text[i]))
            i += 1

    return tokens


def _render(tokens):
    """
    Render tokenized phonemes into Devanagari using proper joining rules.

    Rules:
      - Consonant + Vowel:              emit consonant + vowel matra
      - Consonant + Consonant:           emit consonant + halant (conjunct)
      - Consonant at end:                emit consonant (inherent schwa)
      - Vowel after Consonant:           emit matra form (handled with C)
      - Vowel at start / after Vowel:    emit independent form

    KEY FIX (June 9, 2026): ALL consecutive consonants now get halant,
    not just doubled consonants. This produces correct conjuncts:
      st → स्त  (not सत)
      vy → व्य  (not वय)
      pr → प्र  (not पर)
    """
    result = []
    n = len(tokens)

    for idx in range(n):
        typ, key = tokens[idx]
        prev_type = tokens[idx - 1][0] if idx > 0 else None
        next_tok = tokens[idx + 1] if idx + 1 < n else None

        if typ == "C":
            deva_consonant = CONSONANT_MAP[key]

            if next_tok and next_tok[0] == "C":
                # Consonant followed by consonant → conjunct via halant
                result.append(deva_consonant + HALANT)
            else:
                # Consonant followed by vowel, unknown, or end → just consonant
                # (vowel matra will be appended by the vowel token)
                result.append(deva_consonant)

        elif typ == "V":
            indep, matra = VOWEL_MAP[key]

            if prev_type == "C":
                # Vowel after consonant → use matra (dependent) form
                if matra:  # 'a' has empty matra (inherent, nothing to add)
                    result.append(matra)
            else:
                # Vowel at start, after another vowel, or after unknown
                result.append(indep)

        else:
            # Unknown character → pass through
            result.append(key)

    return "".join(result)


def apply_phoneme_rules(token):
    """
    Convert a romanized token to Devanagari using character-level phoneme rules.

    This is the LAST RESORT transliterator — used only when:
      1. IndicXlit is unavailable or fails
      2. The token is not in the frequency map

    The result won't be perfect for all words (especially long/short vowel
    ambiguity), but provides a reasonable best-guess that is significantly
    better than the naive per-character approach.

    Args:
        token: Romanized Marlish/Marathi word (lowercase expected)

    Returns:
        Devanagari string (best-effort transliteration)
    """
    tokens = _tokenize(token)
    return _render(tokens)


# ─────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_words = [
        # Basic words
        ("udya", "उद्य — expected उद्या (long aa)"),
        ("kay", "काय — expected काय"),
        ("ahe", "अहे — expected आहे (long aa)"),
        ("mitra", "मितर — expected मित्र (conjunct)"),
        ("kasa", "कस — expected कसा (long aa)"),
        ("ghar", "घर — expected घर"),
        ("khup", "खुप — expected खूप (long uu)"),
        ("nahi", "नहि — expected नाही (long aa+ii)"),
        # Words that previously produced garbage
        ("haslo", "हसलो ✅"),
        ("nako", "नको ✅"),
        ("vajle", "वजले ✅ (close)"),
        ("basun", "बसुन ✅ (close)"),
        ("honar", "होनर ✅ (close)"),
        ("mhantos", "म्हनतोस ✅ (close)"),
        ("challay", "चल्लय ✅ (close)"),
    ]

    print("Phoneme Rule Transliteration Test (with matra logic):")
    print("-" * 55)
    for word, note in test_words:
        deva = apply_phoneme_rules(word)
        print(f"  {word:15s} → {deva:15s}  ({note})")
