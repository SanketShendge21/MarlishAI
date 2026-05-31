"""
Minimal pure-Python IndicProcessor — adapted from IndicTransToolkit/processor.pyx
Handles the essential preprocessing for IndicTrans2 without Cython compilation.

Only implements preprocess_batch() and postprocess_batch() for inference.
"""

import re
from indicnlp.tokenize import indic_tokenize, indic_detokenize
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from sacremoses import MosesPunctNormalizer, MosesTokenizer, MosesDetokenizer
from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator


class IndicProcessor:
    """Pure Python IndicProcessor for IndicTrans2 inference."""

    def __init__(self, inference=True):
        self.inference = inference

        self._flores_codes = {
            "asm_Beng": "as", "awa_Deva": "hi", "ben_Beng": "bn",
            "bho_Deva": "hi", "brx_Deva": "hi", "doi_Deva": "hi",
            "eng_Latn": "en", "gom_Deva": "kK", "gon_Deva": "hi",
            "guj_Gujr": "gu", "hin_Deva": "hi", "hne_Deva": "hi",
            "kan_Knda": "kn", "kas_Arab": "ur", "kas_Deva": "hi",
            "kha_Latn": "en", "lus_Latn": "en", "mag_Deva": "hi",
            "mai_Deva": "hi", "mal_Mlym": "ml", "mar_Deva": "mr",
            "mni_Beng": "bn", "mni_Mtei": "hi", "npi_Deva": "ne",
            "ory_Orya": "or", "pan_Guru": "pa", "san_Deva": "hi",
            "sat_Olck": "or", "snd_Arab": "ur", "snd_Deva": "hi",
            "tam_Taml": "ta", "tel_Telu": "te", "urd_Arab": "ur",
            "unr_Deva": "hi",
        }

        # Digit translation table (Indic digits → Arabic)
        digits_dict = {
            "\u09e6": "0", "\u0ae6": "0", "\u0ce6": "0", "\u0966": "0",
            "\u0660": "0", "\uabf0": "0", "\u0b66": "0", "\u0a66": "0",
            "\u1c50": "0", "\u06f0": "0",
            "\u09e7": "1", "\u0ae7": "1", "\u0967": "1", "\u0ce7": "1",
            "\u06f1": "1", "\uabf1": "1", "\u0b67": "1", "\u0a67": "1",
            "\u1c51": "1", "\u0c67": "1",
            "\u09e8": "2", "\u0ae8": "2", "\u0968": "2", "\u0ce8": "2",
            "\u06f2": "2", "\uabf2": "2", "\u0b68": "2", "\u0a68": "2",
            "\u1c52": "2", "\u0c68": "2",
            "\u09e9": "3", "\u0ae9": "3", "\u0969": "3", "\u0ce9": "3",
            "\u06f3": "3", "\uabf3": "3", "\u0b69": "3", "\u0a69": "3",
            "\u1c53": "3", "\u0c69": "3",
            "\u09ea": "4", "\u0aea": "4", "\u096a": "4", "\u0cea": "4",
            "\u06f4": "4", "\uabf4": "4", "\u0b6a": "4", "\u0a6a": "4",
            "\u1c54": "4", "\u0c6a": "4",
            "\u09eb": "5", "\u0aeb": "5", "\u096b": "5", "\u0ceb": "5",
            "\u06f5": "5", "\uabf5": "5", "\u0b6b": "5", "\u0a6b": "5",
            "\u1c55": "5", "\u0c6b": "5",
            "\u09ec": "6", "\u0aec": "6", "\u096c": "6", "\u0cec": "6",
            "\u06f6": "6", "\uabf6": "6", "\u0b6c": "6", "\u0a6c": "6",
            "\u1c56": "6", "\u0c6c": "6",
            "\u09ed": "7", "\u0aed": "7", "\u096d": "7", "\u0ced": "7",
            "\u06f7": "7", "\uabf7": "7", "\u0b6d": "7", "\u0a6d": "7",
            "\u1c57": "7", "\u0c6d": "7",
            "\u09ee": "8", "\u0aee": "8", "\u096e": "8", "\u0cee": "8",
            "\u06f8": "8", "\uabf8": "8", "\u0b6e": "8", "\u0a6e": "8",
            "\u1c58": "8", "\u0c6e": "8",
            "\u09ef": "9", "\u0aef": "9", "\u096f": "9", "\u0cef": "9",
            "\u06f9": "9", "\uabf9": "9", "\u0b6f": "9", "\u0a6f": "9",
            "\u1c59": "9", "\u0c6f": "9",
        }
        self._digits_translation_table = str.maketrans(digits_dict)

        # Regex patterns
        self._MULTISPACE_REGEX = re.compile(r"[ ]{2,}")
        self._DIGIT_SPACE_PERCENT = re.compile(r"(\d) %")
        self._DOUBLE_QUOT_PUNC = re.compile(r"\"([,.])")
        self._DIGIT_NBSP_DIGIT = re.compile(r"(\d) (\d)")
        self._END_BRACKET_SPACE_PUNC_REGEX = re.compile(r"\) ([.!:?;,])")

        # Punctuation replacements
        self._PUNC_REPLACEMENTS = [
            (r"(\.+)", r" \1 "),
            (r"(\,+)", r" \1 "),
            (r"(\!+)", r" \1 "),
            (r"(\?+)", r" \1 "),
            (r"\(", r" ( "),
            (r"\)", r" ) "),
            (r"\;", r" ; "),
            (r"\:", r" : "),
            (r"\"", r' " '),
            (r"\/", r" / "),
            (r"\[", r" [ "),
            (r"\]", r" ] "),
        ]

        self._INDIC_FAILURE_CASES = [
            "ke", "se", "ko", "ka", "ki", "me",
            "ne", "ho", "hai", "hain", "ya", "na",
        ]

        # Placeholder patterns for URLs, numbers, emails
        self._URL_PATTERN = re.compile(
            r"\b(?:https?://|www\.)\S+\b"
        )
        self._NUMERAL_PATTERN = re.compile(
            r"(?:[-+]?\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?)"
        )
        self._EMAIL_PATTERN = re.compile(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        )
        self._OTHER_PATTERN = re.compile(
            r"[a-zA-Z0-9]+"
        )

        # Moses tools (for English)
        self._en_tok = MosesTokenizer(lang="en")
        self._en_normalizer = MosesPunctNormalizer()
        self._en_detok = MosesDetokenizer(lang="en")
        self._xliterator = UnicodeIndicTransliterator()

    def _normalize_indic(self, line, lang):
        normalizer = IndicNormalizerFactory().get_normalizer(lang)
        return normalizer.normalize(line)

    def _wrap_with_placeholders(self, s, lang):
        """Replace URLs, emails, numbers with placeholder tokens."""
        # Simplified — just return the text as-is for our use case
        return s, {}

    def _apply_indic_normalizations(self, sent, lang):
        # Normalize Indic text
        iso_lang = self._flores_codes.get(lang, "hi")
        sent = self._normalize_indic(sent.strip(), iso_lang)

        # Translate Indic digits to ASCII
        sent = sent.translate(self._digits_translation_table)

        # Tokenize Indic text
        sent = " ".join(indic_tokenize.trivial_tokenize(sent, iso_lang))

        return sent

    def _apply_en_normalizations(self, sent):
        # Normalize and tokenize English
        sent = self._en_normalizer.normalize(sent.strip())
        sent = " ".join(self._en_tok.tokenize(sent, escape=False))
        return sent

    def preprocess_batch(self, batch, src_lang, tgt_lang, is_target=False):
        """
        Preprocess a batch of sentences for IndicTrans2.
        """
        processed = []
        lang = tgt_lang if is_target else src_lang
        iso_lang = self._flores_codes.get(lang, "")

        for sent in batch:
            sent = sent.strip()

            # Apply language-specific normalizations
            if lang == "eng_Latn":
                sent = self._apply_en_normalizations(sent)
            else:
                sent = self._apply_indic_normalizations(sent, lang)

            # Clean up whitespace
            sent = self._MULTISPACE_REGEX.sub(" ", sent).strip()

            processed.append(sent)

        return processed

    def postprocess_batch(self, batch, lang, common_lang="hin_Deva"):
        """
        Postprocess a batch of translated sentences.
        """
        processed = []
        iso_lang = self._flores_codes.get(lang, "")

        for sent in batch:
            sent = sent.strip()

            # Detokenize
            if lang == "eng_Latn":
                sent = self._en_detok.detokenize(sent.split())
            else:
                sent = indic_detokenize.trivial_detokenize(sent, iso_lang)

            # Clean whitespace
            sent = self._MULTISPACE_REGEX.sub(" ", sent).strip()

            processed.append(sent)

        return processed
