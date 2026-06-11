"""
Token Classifier for Marlish Transliteration Pipeline

Classifies each token in a mixed-code sentence as:
  - ENGLISH:    Known English loanword → pass through unchanged
  - DEVANAGARI: Already in Devanagari script → pass through unchanged
  - NUMERIC:    Numbers/punctuation → pass through unchanged
  - MARLISH:    Romanized Marathi → needs transliteration to Devanagari
"""

import re

# ─────────────────────────────────────────────────────────
# English passthrough set
# These words commonly appear in Marlish/Hinglish chat as-is.
# Expanded from our existing dictionary JSON files.
# ─────────────────────────────────────────────────────────
ENGLISH_PASSTHROUGH = {
    # Greetings & social
    "hi", "hello", "hey", "bye", "goodbye", "ok", "okay", "yes", "no",
    "please", "thanks", "thank", "sorry", "welcome",

    # Slang & filler
    "bro", "dude", "yaar", "man", "guys", "lol", "omg", "wtf", "bruh",
    "cool", "chill", "vibe", "vibes", "lit", "fire", "sick", "dope",

    # Common loanwords used in Indian English
    "scene", "party", "college", "school", "office", "meeting", "class",
    "phone", "mobile", "laptop", "computer", "internet", "wifi",
    "bus", "train", "auto", "taxi", "uber", "ola",
    "movie", "film", "song", "video", "game", "cricket", "match",
    "food", "pizza", "burger", "coffee", "tea", "water",
    "time", "date", "plan", "cancel", "confirm", "done", "ready",
    "busy", "free", "late", "early", "fast", "slow",
    "hospital", "doctor", "medicine",
    "money", "cash", "bank", "atm", "upi",
    "shop", "mall", "market",
    "friend", "brother", "sister",
    "message", "call", "text", "whatsapp", "instagram", "facebook",

    # Additional loanwords commonly used in Indian chat
    "shopping", "book", "photo", "photos", "boring", "exam", "exams",
    "hotel", "gym", "bike", "car", "tv", "app",
    "online", "offline", "download", "upload",
    "battery", "charger", "network", "data", "signal",
    "selfie", "status", "story", "reel",
    "like", "comment", "follow", "post", "block",
    "profile", "account", "login", "logout", "password",
    "link", "page", "group", "chat",
    "meme", "gif", "emoji", "sticker",
    "nice", "great", "good", "bad", "best", "worst",
    "happy", "sad", "angry", "tired", "bored", "excited",
    "boss", "sir", "madam",
    "ticket", "pass", "seat", "bag",
    "order", "delivery", "payment",
    "reply", "forward", "edit", "delete", "copy", "paste",

    # Conjunctions & prepositions sometimes used in English within Marlish
    "and", "but", "or", "for", "with", "from", "to", "at", "in", "on",
    "the", "a", "an", "is", "are", "was", "were", "will", "can",
    "not", "so", "very", "much", "too", "also",

    # Common verbs used in English within code-mixed text
    "start", "stop", "wait", "come", "go", "try", "check", "send",
    "share", "join", "leave", "help",
}

# Devanagari Unicode range: 0x0900–0x097F
_DEVANAGARI_RE = re.compile(r'[\u0900-\u097F]')

# Punctuation / special characters
_PUNCT_RE = re.compile(r'^[^\w]+$')


def classify_token(token: str, context: list = None) -> str:
    """
    Classify a single token.

    Args:
        token:   The word/token to classify.
        context: (Optional) List of surrounding tokens for future
                 context-aware disambiguation (e.g., 'kay' in Hinglish
                 vs Marlish). Currently unused — reserved for Phase 2
                 enhancements.

    Returns:
        One of: 'ENGLISH', 'DEVANAGARI', 'NUMERIC', 'PUNCTUATION', 'MARLISH'
    """
    stripped = token.strip()

    if not stripped:
        return 'PUNCTUATION'

    # Already Devanagari? Pass through.
    if _DEVANAGARI_RE.search(stripped):
        return 'DEVANAGARI'

    # Pure number? Pass through.
    if stripped.isdigit():
        return 'NUMERIC'

    # Punctuation only? Pass through.
    if _PUNCT_RE.match(stripped):
        return 'PUNCTUATION'

    # Known English word? Pass through.
    if stripped.lower() in ENGLISH_PASSTHROUGH:
        return 'ENGLISH'

    # Default: assume it's romanized Marlish that needs transliteration
    return 'MARLISH'


def classify_sentence(sentence: str) -> list:
    """
    Classify all tokens in a sentence.

    Returns:
        List of (token, classification) tuples.
        Example: [("udya", "MARLISH"), ("kay", "MARLISH"), ("scene", "ENGLISH")]
    """
    tokens = sentence.split()
    results = []
    for token in tokens:
        classification = classify_token(token, context=tokens)
        results.append((token, classification))
    return results


# ─────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        "udya kay scene ahe bro",
        "mi college la jato ahe",
        "kasa ahes mitra",
        "मला माहित नाही",
        "123 hello काय",
        "party ahe kal ratra",
    ]
    for sentence in test_cases:
        print(f"\nInput: {sentence}")
        for token, cls in classify_sentence(sentence):
            print(f"  {token:20s} → {cls}")
