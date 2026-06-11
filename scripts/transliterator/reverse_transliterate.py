"""
Reverse Transliteration: Devanagari → Romanized (Marlish/Hinglish style)

Converts Devanagari script output from NLLB back to natural romanized
chat-style text (e.g., "तू कुठे आहेस" → "tu kuthe ahes").

Two-tier approach:
  1. Word-level lookup (reverse of the seed map — highest accuracy)
  2. Character-level Devanagari → Latin rules (fallback for unknown words)
"""

import re

# ─────────────────────────────────────────────────────────
# Devanagari digit → ASCII digit mapping
# ─────────────────────────────────────────────────────────
DEVA_DIGIT_MAP = {
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
}

# ─────────────────────────────────────────────────────────
# Character-level Devanagari → Latin mapping
# Maps each Devanagari character/matra to its natural romanized form
# ─────────────────────────────────────────────────────────

# Vowels (independent forms)
VOWEL_MAP = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee",
    "उ": "u", "ऊ": "oo", "ऋ": "ru",
    "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
    "अं": "an", "अः": "ah",
}

# Vowel signs (matras — attached to consonants)
MATRA_MAP = {
    "ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
    "ं": "n", "ः": "h", "ँ": "n",
    "ृ": "ru",
}

# Consonants
CONSONANT_MAP = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "n",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v", "w": "w",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "ळ": "l", "क्ष": "ksh", "ज्ञ": "dnya",
}

# Halant (virama) — suppresses inherent 'a'
HALANT = "्"

# Nukta consonants (for loan words)
NUKTA_MAP = {
    "क़": "q", "ख़": "kh", "ग़": "gh", "ज़": "z", "फ़": "f",
    "ड़": "d", "ढ़": "dh",
}

# Avagraha
AVAGRAHA = "ऽ"


# Canonical romanized forms — when multiple romanized spellings map to
# the same Devanagari, this decides which one to use for reverse output.
# Only need to list words that have ambiguous variants in the seed map.
PREFERRED_REVERSE = {
    "आहे": "ahe",
    "नाही": "nahi",
    "नाव": "nav",
    "पाणी": "pani",
    "काम": "kaam",
    "आत्ता": "atta",
    "आहेस": "ahes",
    "करतो": "karto",
    "जेवण": "jevan",
    "बघ": "bagh",
}


def _build_reverse_word_map(seed_map: dict) -> dict:
    """
    Invert the seed map: {devanagari: romanized}.
    Uses PREFERRED_REVERSE for words with multiple variants.
    For others, keeps the first encountered form.
    """
    reverse = {}
    for roman, deva in seed_map.items():
        if deva in PREFERRED_REVERSE:
            reverse[deva] = PREFERRED_REVERSE[deva]
        elif deva not in reverse:
            reverse[deva] = roman
    return reverse


def _devanagari_to_roman_char(text: str) -> str:
    """
    Character-level Devanagari → romanized conversion.
    Handles consonant clusters, matras, and halant.
    """
    result = []
    i = 0
    chars = list(text)
    length = len(chars)

    while i < length:
        char = chars[i]

        # Check nukta consonants (2-char sequences)
        if i + 1 < length and char + chars[i + 1] in NUKTA_MAP:
            result.append(NUKTA_MAP[char + chars[i + 1]])
            i += 2
            # Check for matra after nukta consonant
            if i < length and chars[i] in MATRA_MAP:
                result.append(MATRA_MAP[chars[i]])
                i += 1
            elif i < length and chars[i] == HALANT:
                i += 1  # suppress inherent 'a'
            else:
                result.append("a")  # inherent vowel
            continue

        # Check conjunct consonants (consonant + halant + consonant)
        if char in CONSONANT_MAP:
            result.append(CONSONANT_MAP[char])
            i += 1

            # Check for halant (virama) — consonant cluster
            while i < length and chars[i] == HALANT:
                i += 1  # skip halant
                if i < length and chars[i] in CONSONANT_MAP:
                    result.append(CONSONANT_MAP[chars[i]])
                    i += 1
                else:
                    break

            # Check for matra (vowel sign)
            if i < length and chars[i] in MATRA_MAP:
                result.append(MATRA_MAP[chars[i]])
                i += 1
            elif i < length and chars[i] == HALANT:
                i += 1  # explicit halant at end — no inherent vowel
            elif i < length and chars[i] not in CONSONANT_MAP and chars[i] not in VOWEL_MAP and chars[i] != " ":
                # Some other character — add inherent 'a' for the consonant
                result.append("a")
            elif i >= length or chars[i] == " ":
                result.append("a")  # word-final inherent vowel
            elif chars[i] in CONSONANT_MAP:
                result.append("a")  # next char is another consonant — inherent 'a'
            elif chars[i] in VOWEL_MAP:
                result.append("a")  # independent vowel follows
            continue

        # Independent vowels
        # Check 2-char vowels first (अं, अः)
        if i + 1 < length and char + chars[i + 1] in VOWEL_MAP:
            result.append(VOWEL_MAP[char + chars[i + 1]])
            i += 2
            continue

        if char in VOWEL_MAP:
            result.append(VOWEL_MAP[char])
            i += 1
            # Check for anusvara/visarga after vowel
            if i < length and chars[i] in MATRA_MAP:
                result.append(MATRA_MAP[chars[i]])
                i += 1
            continue

        # Standalone matras (shouldn't happen in well-formed text, but handle gracefully)
        if char in MATRA_MAP:
            result.append(MATRA_MAP[char])
            i += 1
            continue

        # Avagraha
        if char == AVAGRAHA:
            i += 1
            continue

        # Pass through everything else (spaces, punctuation, numbers, Latin chars)
        result.append(char)
        i += 1

    return "".join(result)


def _convert_deva_digits(text: str) -> str:
    """Convert Devanagari digits (०-९) to ASCII digits (0-9)."""
    for deva, ascii_d in DEVA_DIGIT_MAP.items():
        text = text.replace(deva, ascii_d)
    return text


def _simplify_romanized(text: str) -> str:
    """
    Simplify overly formal/literal romanized output to match
    natural chat-style spelling conventions.

    Examples:
        kanyakumaree → kanyakumari
        darshaneeya  → darshaniya
        mndira       → mandira
        sthalh       → sthal
    """
    # ee at word boundary → i (kanyakumaree → kanyakumari)
    text = re.sub(r'ee\b', 'i', text)
    # oo at word boundary → u (except standalone "oo")
    text = re.sub(r'(?<=\w)oo\b', 'u', text)
    # Double 'aa' at end → 'a' (yaatraa → yatra)
    text = re.sub(r'aa\b', 'a', text)
    # 'nh' → 'n' when not part of a real cluster
    text = re.sub(r'\bnh\b', 'n', text)
    # Clean up stray 'h' after consonant clusters at end: "sthalh" → "sthal"
    text = re.sub(r'(\w)h\b', lambda m: m.group(1) if m.group(1) in 'lnr' else m.group(0), text)
    return text


def reverse_transliterate(devanagari_text: str, seed_map: dict = None) -> str:
    """
    Convert Devanagari text to natural romanized chat-style text.

    Args:
        devanagari_text: Text in Devanagari script (e.g., "तू कुठे आहेस")
        seed_map: Optional forward map {romanized: devanagari} for word-level lookup

    Returns:
        Romanized text (e.g., "tu kuthe ahes")
    """
    if not devanagari_text:
        return ""

    # Build reverse word map if seed map provided
    reverse_word_map = {}
    if seed_map:
        reverse_word_map = _build_reverse_word_map(seed_map)

    # Split into tokens (preserve punctuation and spaces)
    tokens = devanagari_text.split()
    result_tokens = []

    for token in tokens:
        # Separate punctuation from the token
        prefix_punct = ""
        suffix_punct = ""
        core = token

        # Strip leading punctuation
        while core and not _is_devanagari(core[0]) and not core[0].isalnum():
            prefix_punct += core[0]
            core = core[1:]

        # Strip trailing punctuation
        while core and not _is_devanagari(core[-1]) and not core[-1].isalnum():
            suffix_punct = core[-1] + suffix_punct
            core = core[:-1]

        if not core:
            result_tokens.append(token)
            continue

        # Tier 1: Word-level lookup (highest accuracy)
        if core in reverse_word_map:
            romanized = reverse_word_map[core]
        else:
            # Tier 2: Character-level conversion
            romanized = _devanagari_to_roman_char(core)

        result_tokens.append(prefix_punct + romanized + suffix_punct)

    # Convert Devanagari digits to ASCII
    result_text = " ".join(result_tokens)
    result_text = _convert_deva_digits(result_text)
    result_text = _simplify_romanized(result_text)
    return result_text


def _is_devanagari(char: str) -> bool:
    """Check if a character is in the Devanagari Unicode block."""
    return "\u0900" <= char <= "\u097F"


# ─────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test without seed map (pure character-level)
    test_cases = [
        ("तू कुठे आहेस", "tu kuthe ahes"),
        ("तुम कहाँ हो", "tum kahaan ho"),
        ("कसा आहेस मित्र", "kasa ahes mitra"),
        ("मला माहित नाही", "mala mahit nahi"),
        ("उद्या काय scene आहे", "udya kay scene ahe"),
    ]

    print("=" * 60)
    print("  Reverse Transliteration — Self Test")
    print("=" * 60)

    for deva, expected in test_cases:
        result = reverse_transliterate(deva)
        status = "✅" if result.lower().strip() == expected.lower().strip() else "⚠️"
        print(f"\n  {status} Input:    {deva}")
        print(f"     Output:   {result}")
        print(f"     Expected: {expected}")

    print("=" * 60)
