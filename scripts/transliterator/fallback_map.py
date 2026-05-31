"""
Fallback Map for Marlish Transliteration Pipeline

Frequency-ranked Marlish (romanized) → Devanagari word map.
This is the SECOND tier of the transliteration pipeline:
  1. IndicXlit (primary, AI-powered)
  2. Fallback Map (this file — fast O(1) lookup)
  3. Phoneme Rules (last resort — character-level conversion)

The map below is a curated seed set. The full map should be built
by running `scripts/build_transliteration_map.py` against the
3.6M-row parquet dataset, which extracts the most frequent
romanized↔Devanagari pairs.

At runtime, `public/transliteration_map.json` (built from the
parquet data) is loaded and merged with this seed map.
"""

import json
import os

# ─────────────────────────────────────────────────────────
# Curated seed map — high-confidence, manually verified
# Covers the ~200 most common Marlish words in chat
# ─────────────────────────────────────────────────────────
SEED_MAP = {
    # ── Pronouns ──
    "mi": "मी",
    "tu": "तू",
    "to": "तो",
    "ti": "ती",
    "te": "ते",
    "tyala": "त्याला",
    "tila": "तिला",
    "amhi": "आम्ही",
    "tumhi": "तुम्ही",
    "apan": "आपण",
    "mala": "मला",
    "tula": "तुला",

    # ── Common verbs ──
    "ahe": "आहे",
    "aahe": "आहे",
    "aye": "आहे",
    "nahi": "नाही",
    "nai": "नाही",
    "hota": "होता",
    "hoti": "होती",
    "hote": "होते",
    "hoil": "होईल",
    "ho": "हो",
    "hoy": "होय",
    "karto": "करतो",
    "karato": "करतो",
    "karti": "करती",
    "karte": "करते",
    "karaycha": "करायचा",
    "kela": "केला",
    "keli": "केली",
    "kele": "केले",
    "jato": "जातो",
    "jate": "जाते",
    "jaa": "जा",
    "ja": "जा",
    "yeto": "येतो",
    "yete": "येते",
    "ye": "ये",
    "ya": "या",
    "ala": "आला",
    "ali": "आली",
    "ale": "आले",
    "gela": "गेला",
    "geli": "गेली",
    "gele": "गेले",
    "deto": "देतो",
    "dete": "देते",
    "de": "दे",
    "gheto": "घेतो",
    "ghete": "घेते",
    "ghe": "घे",
    "baghto": "बघतो",
    "bagh": "बघ",
    "bagh": "बघ",
    "bolto": "बोलतो",
    "bol": "बोल",
    "sangto": "सांगतो",
    "sang": "सांग",
    "khato": "खातो",
    "kha": "खा",
    "pito": "पितो",
    "pi": "पी",
    "basla": "बसला",
    "bas": "बस",
    "uthla": "उठला",
    "uth": "उठ",
    "jevla": "जेवला",
    "jevli": "जेवली",
    "jevle": "जेवले",

    # ── Question words ──
    "kay": "काय",
    "ka": "का",
    "kasa": "कसा",
    "kashi": "कशी",
    "kase": "कसे",
    "kuthe": "कुठे",
    "kadhi": "कधी",
    "kon": "कोण",
    "kiti": "किती",

    # ── Time ──
    "aaj": "आज",
    "udya": "उद्या",
    "kal": "काल",
    "aata": "आता",
    "nantar": "नंतर",
    "atta": "आत्ता",
    "sakali": "सकाळी",
    "sandhyakali": "संध्याकाळी",
    "ratri": "रात्री",
    "ratra": "रात्र",
    "dupari": "दुपारी",

    # ── Common nouns ──
    "ghar": "घर",
    "gharala": "घराला",
    "ghari": "घरी",
    "paani": "पाणी",
    "pani": "पाणी",
    "jevana": "जेवण",
    "jevan": "जेवण",
    "kaam": "काम",
    "kam": "काम",
    "mitra": "मित्र",
    "bhau": "भाऊ",
    "tai": "ताई",
    "dada": "दादा",
    "aai": "आई",
    "baba": "बाबा",
    "dost": "दोस्त",
    "lok": "लोक",
    "mulga": "मुलगा",
    "mulgi": "मुलगी",
    "mule": "मुले",
    "nav": "नाव",       # name (NOT नव = new)
    "naav": "नाव",
    "paisa": "पैसा",
    "paise": "पैसे",
    "vel": "वेळ",        # time
    "divas": "दिवस",    # day
    "rasta": "रस्ता",    # road
    "gaadi": "गाडी",    # vehicle
    "phone": "फोन",
    "photo": "फोटो",

    # ── Possessive pronouns ──
    "tuza": "तुझा",     # your (masc)
    "tuzi": "तुझी",     # your (fem)
    "tuze": "तुझे",     # your (neut)
    "mazha": "माझा",    # my (masc)
    "mazi": "माझी",     # my (fem)
    "maze": "माझे",     # my (neut)
    "tyacha": "त्याचा", # his
    "tyachi": "त्याची",
    "tyache": "त्याचे",
    "ticha": "तिचा",    # her
    "tichi": "तिची",
    "tiche": "तिचे",
    "amcha": "आमचा",    # our
    "tumcha": "तुमचा",  # your (formal)

    # ── Adjectives & adverbs ──
    "khup": "खूप",
    "chhan": "छान",
    "mast": "मस्त",
    "bara": "बरा",
    "changla": "चांगला",
    "changali": "चांगली",
    "vaait": "वाईट",
    "motha": "मोठा",
    "lahan": "लहान",
    "haluk": "हळूक",
    "lavkar": "लवकर",
    "aadhi": "आधी",
    "ekdum": "एकदम",

    # ── Postpositions & particles ──
    "la": "ला",
    "cha": "चा",
    "chi": "ची",
    "che": "चे",
    "madhe": "मध्ये",
    "var": "वर",
    "khali": "खाली",
    "paryant": "पर्यंत",
    "saathi": "साठी",
    "sobat": "सोबत",
    "barobar": "बरोबर",
    "ani": "आणि",
    "pan": "पण",
    "mhanun": "म्हणून",
    "ki": "की",
    "tar": "तर",
    "re": "रे",
    "na": "ना",
    "ga": "ग",

    # ── Numbers ──
    "ek": "एक",
    "don": "दोन",
    "teen": "तीन",
    "char": "चार",
    "paach": "पाच",

    # ── Common phrases (single-token variants) ──
    "bhetel": "भेटेल",
    "bhet": "भेट",
    "bhetla": "भेटला",
    "bhetli": "भेटली",
    "mahit": "माहित",
    "samjla": "समजला",
    "samjli": "समजली",
    "chalel": "चालेल",
    "chalto": "चालतो",
    "chal": "चल",
    "thamba": "थांबा",
    "thamb": "थांब",
    "ahes": "आहेस",
    "ahet": "आहेत",

    # ── Demonstratives ──
    "he": "हे",        # this (neuter)
    "ha": "हा",        # this (masculine)
    "hya": "ह्या",     # this (oblique)
    "tya": "त्या",     # that (oblique)

    # ── Marathi म्ह- prefix verbs ──
    "mhanto": "म्हणतो",
    "mhantos": "म्हणतोस",
    "mhante": "म्हणते",
    "mhanala": "म्हणाला",
    "mhanali": "म्हणाली",
    "mhantat": "म्हणतात",

    # ── Additional common verbs ──
    "honar": "होणार",
    "nako": "नको",
    "nakos": "नकोस",
    "basun": "बसून",
    "lagla": "लागला",
    "lagli": "लागली",
    "lagali": "लागली",
    "lagale": "लागले",
    "takla": "टाकला",
    "takli": "टाकली",
    "takle": "टाकले",
    "vatla": "वाटला",
    "vatli": "वाटली",
    "vatle": "वाटले",
    "haslo": "हसलो",
    "hasli": "हसली",
    "hasle": "हसले",
    "jaycha": "जायचा",
    "jauycha": "जाऊयचा",
    "yaycha": "यायचा",
    "vajle": "वाजले",
    "challay": "चाल्लय",
    "bhetuyaa": "भेटूया",
    "piyaycha": "पियायचा",
    "tayar": "तयार",

    # ── Additional common nouns / adj ──
    "bhuk": "भूक",
    "thoda": "थोडा",
    "thodi": "थोडी",
    "thodya": "थोड्या",
}


def load_dataset_map(map_path: str = None) -> dict:
    """
    Load the frequency-ranked transliteration map built from the parquet dataset.
    Falls back to SEED_MAP if the JSON file doesn't exist yet.

    Args:
        map_path: Path to transliteration_map.json (defaults to public/ folder)

    Returns:
        Dict of {romanized_lower: devanagari}
    """
    if map_path is None:
        # Default path relative to project root
        map_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "public", "transliteration_map.json"
        )

    combined = {}

    if os.path.exists(map_path):
        try:
            with open(map_path, "r", encoding="utf-8") as f:
                dataset_map = json.load(f)
            # Load dataset entries first (frequency-ranked, broad coverage)
            combined.update(dataset_map)
            print(f"  [fallback_map] Loaded {len(dataset_map)} entries from {map_path}")
        except Exception as e:
            print(f"  [fallback_map] Warning: Could not load {map_path}: {e}")
    else:
        print(f"  [fallback_map] No dataset map found at {map_path}, using seed map only ({len(SEED_MAP)} entries)")

    # Seed map OVERRIDES dataset — curated Marathi forms take priority
    # over frequency-ranked entries (which may have Hindi forms like
    # नहीं instead of Marathi नाही)
    combined.update(SEED_MAP)

    return combined


def lookup(token: str, transliteration_map: dict = None) -> str | None:
    """
    Look up a romanized token in the fallback map.

    Returns:
        Devanagari string if found, None otherwise.
    """
    if transliteration_map is None:
        transliteration_map = SEED_MAP

    return transliteration_map.get(token.lower().strip())


# ─────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Seed map size: {len(SEED_MAP)} entries")
    print("\nSample lookups:")
    test_words = ["udya", "kay", "ahe", "mitra", "unknown_word", "khup", "ghar"]
    for word in test_words:
        result = lookup(word)
        status = result if result else "❌ NOT FOUND"
        print(f"  {word:15s} → {status}")
