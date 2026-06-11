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

    # ── Missing words from quality tests (June 2026) ──
    # Test 5: "Jevay" food/eating words
    "jevay": "जेवाय",         # to eat (infinitive colloquial)
    "jevayla": "जेवायला",     # for eating / to eat
    "jevlas": "जेवलास",       # did you eat? (2nd person)
    "jevaycha": "जेवायचा",   # about eating
    "jevto": "जेवतो",        # eats (masc)
    "jevte": "जेवते",        # eats (fem)
    "jevat": "जेवात",        # while eating

    # Test 2: "yeshil" will come/go forms
    "yeshil": "येशील",        # will you come
    "yenar": "येणार",         # going to come
    "yein": "येईन",          # I will come
    "yeil": "येईल",          # he/she will come
    "yeu": "येऊ",            # let's come
    "yeun": "येऊन",          # having come
    "janar": "जाणार",         # going to go
    "janar ahe": "जाणार आहे",
    "jain": "जाईन",          # I will go
    "jail": "जाईल",          # he/she will go
    "jayche": "जायचे",       # to go (neuter)

    # Test 8: "vaat baghte" = waiting (NOT cattle)
    "vaat": "वाट",            # path / waiting (NOT वात = wick)
    "vaato": "वाटो",
    "baghte": "बघते",         # watches/waits (fem)
    "baghto": "बघतो",         # watches/waits (masc)
    "baghtoy": "बघतोय",       # is watching (masc ongoing)
    "baghtey": "बघतेय",       # is watching (fem ongoing)
    "thaklo": "थकलो",         # tired (1st person masc)
    "thakli": "थकली",         # tired (1st person fem)
    "thakla": "थकला",         # tired (3rd person masc)

    # Test 12: Indian food words (NLLB doesn't know these)
    "poha": "पोहा",           # flattened rice dish
    "vada": "वडा",            # fried snack
    "pav": "पाव",             # bread
    "bhaji": "भाजी",          # vegetable curry
    "dal": "डाळ",             # lentils
    "roti": "रोटी",           # flatbread
    "chai": "चाय",            # tea
    "puri": "पुरी",            # fried bread
    "samosa": "समोसा",
    "chutney": "चटणी",

    # Test 6: "urgent lagto" — common urgency/feeling words
    "urgent": "अर्जंट",       # keep as-is loanword
    "lagto": "लागतो",         # feels / is needed
    "lagte": "लागते",
    "pahije": "पाहिजे",       # is needed / want
    "hava": "हवा",            # is needed (informal)
    "havi": "हवी",

    # Common chat words still missing
    "bhai": "भाई",            # brother/bro
    "yaar": "यार",            # dude
    "bro": "ब्रो",
    "scene": "सीन",           # scene/plan
    "busy": "बिझी",
    "boring": "बोरिंग",
    "meeting": "मीटिंग",
    "college": "कॉलेज",
    "office": "ऑफिस",
    "exam": "परीक्षा",
    "party": "पार्टी",
    "coffee": "कॉफी",
    "train": "ट्रेन",
    "picnic": "पिकनिक",
    "call": "कॉल",
    "mood": "मूड",

    # Common Marathi verb forms still missing
    "baher": "बाहेर",          # outside
    "thandi": "थंडी",         # cold
    "khush": "खुश",           # happy
    "pass": "पास",            # pass (exam)
    "zalo": "झालो",           # became / happened (1st person)
    "zala": "झाला",           # became / happened (masc)
    "zali": "झाली",           # became / happened (fem)
    "zale": "झाले",           # became / happened (neut/pl)

    # Hindi words for Hinglish support
    "kal": "कल",              # yesterday/tomorrow (Hindi)
    "hai": "है",              # is (Hindi)
    "hain": "हैं",            # are (Hindi)
    "kuch": "कुछ",            # something (Hindi)
    "mat": "मत",              # don't (Hindi)
    "mera": "मेरा",           # my (Hindi)
    "tera": "तेरा",           # your (Hindi)
    "kidhar": "किधर",         # where (Hindi colloquial)
    "chalte": "चलते",         # let's go / walk (Hindi)
    "dekhne": "देखने",        # to watch (Hindi)
    "padha": "पढ़ा",          # studied (Hindi)
    "aaya": "आया",            # came (Hindi)
    "banaya": "बनाया",        # made (Hindi)
    "tumhare": "तुम्हारे",    # your (Hindi)

    # ── Carnival Tours test failures (June 9, 2026) ──
    # Formal/travel Marathi words
    "samavishta": "समाविष्ट",       # included
    "vyavastha": "व्यवस्था",        # arrangement
    "sthanik": "स्थानिक",           # local
    "sthal": "स्थळ",               # place/site
    "sthaldarshan": "स्थलदर्शन",    # sightseeing
    "darshan": "दर्शन",             # visit/viewing
    "shakahari": "शाकाहारी",        # vegetarian
    "vaiyaktik": "वैयक्तिक",        # personal
    "mukkam": "मुक्काम",            # stay/halt
    "pravas": "प्रवास",             # journey/travel
    "poch": "पोच",                 # arrive
    "ayojit": "आयोजित",            # organized
    "dinank": "दिनांक",             # date
    "sahal": "सहल",                # tour/trip
    "prashtan": "प्रस्थान",         # departure
    "kharredi": "खरेदी",           # shopping
    "divas": "दिवस",               # day
    "ratri": "रात्री",               # night
    "relve": "रेल्वे",              # railway
    "sleeper": "स्लीपर",
    "shuddha": "शुद्ध",             # pure
    "nashta": "नाष्टा",             # breakfast
    "adhik": "अधिक",               # more/extra
    "dyave": "द्यावे",              # should give
    "lagtil": "लागतील",             # will be needed
    "asalyaas": "असल्यास",          # if there is
    "shaharantar": "शहरांतर",         # intercity
    "jata": "जाता",                # going
    "yeta": "येता",                # coming
    "jevan": "जेवण",               # food/meal
    "vel": "वेळ",                  # time/times
    "chaha": "चहा",                # tea
    "mandir": "मंदिर",              # temple
    "bich": "बीच",                 # beach
    "samudra": "समुद्र",             # ocean

    # Hindi formal/travel words
    "sthaniya": "स्थानीय",          # local (Hindi)
    "vyaktigat": "व्यक्तिगत",       # personal (Hindi)
    "bhojan": "भोजन",             # food/meal (Hindi)
    "yatra": "यात्रा",              # journey (Hindi)
    "shamil": "शामिल",             # included (Hindi)
    "pahunchna": "पहुँचना",          # to arrive (Hindi)
    "thehra": "ठहराव",             # stay (Hindi)
    "shahrantar": "शहरांतर्गत",       # intercity (Hindi)
    "kamra": "कमरा",               # room (Hindi)
    "chahiye": "चाहिए",            # want/need (Hindi)
    "honge": "होंगे",              # will be (Hindi)
    "dene": "देने",                # to give (Hindi)
    "baar": "बार",                 # times (Hindi)
    "aane": "आने",                 # coming (Hindi)
    "jaane": "जाने",               # going (Hindi)
    "tarikhein": "तारीखें",          # dates (Hindi)
    "dwara": "द्वारा",              # by/through (Hindi)

    # Hinglish common words
    "toh": "तो",                   # then/so
    "koi": "कोई",                  # someone/anyone
    "nahi": "नाही",                # no/not
    "aur": "और",                   # and (Hindi)
    "mein": "में",                 # in (Hindi)
    "ke": "के",                    # of (Hindi)
    "se": "से",                    # from (Hindi)
    "pe": "पे",                    # on (Hindi colloquial)
    "ne": "ने",                    # by (Hindi)
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
