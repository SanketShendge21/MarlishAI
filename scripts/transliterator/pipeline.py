"""
Marlish Transliteration Pipeline — Core Orchestrator

3-tier transliteration strategy:
  Tier 1: IndicXlit (AI-powered, highest accuracy)
  Tier 2: Fallback Map (frequency-ranked word lookup, O(1))
  Tier 3: Phoneme Rules (character-level, last resort)

Usage:
    from scripts.transliterator.pipeline import MarlishTransliterationPipeline

    pipeline = MarlishTransliterationPipeline()
    result = pipeline.transliterate("udya kay scene ahe bro")
    # → "उद्या काय scene आहे bro"
"""

from .token_classifier import classify_sentence
from .fallback_map import load_dataset_map, lookup
from .phoneme_rules import apply_phoneme_rules


class MarlishTransliterationPipeline:
    """
    Transliterates romanized Marlish text to Devanagari while preserving
    English loanwords, numbers, and existing Devanagari.
    """

    def __init__(self, map_path: str = None, use_indicxlit: bool = False):
        """
        Args:
            map_path:       Path to transliteration_map.json (auto-detected if None)
            use_indicxlit:  Whether to try IndicXlit as Tier 1 (requires separate install)
        """
        print("[Pipeline] Initializing Marlish Transliteration Pipeline...")

        # Load fallback map (seed + dataset-generated)
        self.transliteration_map = load_dataset_map(map_path)
        print(f"[Pipeline] Fallback map loaded: {len(self.transliteration_map)} entries")

        # IndicXlit (Tier 1) — optional, not available on Windows without fairseq
        self.indicxlit = None
        if use_indicxlit:
            try:
                from ai4bharat.transliteration import XlitEngine
                self.indicxlit = XlitEngine("mr", beam_width=4)
                print("[Pipeline] IndicXlit loaded successfully (Tier 1 active)")
            except ImportError:
                print("[Pipeline] IndicXlit not available — using Tier 2 + 3 only")
            except Exception as e:
                print(f"[Pipeline] IndicXlit failed to load: {e} — using Tier 2 + 3 only")

        self.stats = {"indicxlit": 0, "fallback_map": 0, "phoneme": 0, "passthrough": 0}

    def transliterate_token(self, token: str) -> str:
        """
        Transliterate a single MARLISH token to Devanagari using the 3-tier strategy.
        """
        # Tier 1: IndicXlit (if available)
        if self.indicxlit is not None:
            try:
                results = self.indicxlit.translit_word(token.lower(), topk=1)
                if results and results.get("mr"):
                    self.stats["indicxlit"] += 1
                    return results["mr"][0]
            except Exception:
                pass  # fall through to Tier 2

        # Tier 2: Fallback map lookup
        map_result = lookup(token, self.transliteration_map)
        if map_result is not None:
            self.stats["fallback_map"] += 1
            return map_result

        # Tier 3: Phoneme rules (last resort)
        self.stats["phoneme"] += 1
        return apply_phoneme_rules(token)

    def transliterate(self, text: str) -> str:
        """
        Transliterate a full sentence.

        English loanwords, numbers, punctuation, and existing Devanagari
        are passed through unchanged. Only MARLISH tokens are transliterated.

        Args:
            text: Mixed-code Marlish input string

        Returns:
            String with Marlish tokens converted to Devanagari
        """
        classified = classify_sentence(text)
        result_tokens = []

        for token, classification in classified:
            if classification == "MARLISH":
                deva = self.transliterate_token(token)
                result_tokens.append(deva)
            else:
                # ENGLISH, DEVANAGARI, NUMERIC, PUNCTUATION — pass through
                self.stats["passthrough"] += 1
                result_tokens.append(token)

        return " ".join(result_tokens)

    def get_stats(self) -> dict:
        """Return transliteration statistics for debugging/benchmarking."""
        return dict(self.stats)

    def reset_stats(self):
        """Reset the stats counters."""
        self.stats = {"indicxlit": 0, "fallback_map": 0, "phoneme": 0, "passthrough": 0}


# ─────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    pipeline = MarlishTransliterationPipeline()

    test_sentences = [
        "udya kay scene ahe bro",
        "mi college la jato ahe",
        "kadhi bhetel re tu",
        "jevla ka nahi",
        "kasa ahes mitra",
        "khup busy aahe mi aata",
        "party ahe kal ratra",
        "mala mahit nahi",
        "tu kuthe ahes",
        "ghar ye bhai",
    ]

    print("\n" + "=" * 60)
    print("  Marlish Transliteration Pipeline — Self Test")
    print("=" * 60)

    for sentence in test_sentences:
        result = pipeline.transliterate(sentence)
        print(f"\n  Input:  {sentence}")
        print(f"  Output: {result}")

    print(f"\n  Stats: {pipeline.get_stats()}")
    print("=" * 60)
