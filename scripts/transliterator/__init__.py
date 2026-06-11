"""
Marlish Transliteration Pipeline

A 3-tier transliteration system for converting romanized Marlish/Marathi
text to Devanagari script, designed for the MarlishAI hybrid architecture.

Usage:
    from scripts.transliterator import MarlishTransliterationPipeline

    pipeline = MarlishTransliterationPipeline()
    result = pipeline.transliterate("udya kay scene ahe bro")
    # → "उद्या काय scene आहे bro"
"""

from .pipeline import MarlishTransliterationPipeline
from .token_classifier import classify_token, classify_sentence
from .fallback_map import lookup, SEED_MAP
from .phoneme_rules import apply_phoneme_rules

__all__ = [
    "MarlishTransliterationPipeline",
    "classify_token",
    "classify_sentence",
    "lookup",
    "SEED_MAP",
    "apply_phoneme_rules",
]
