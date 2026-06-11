"""
Build Transliteration Map from Parquet Datasets

Extracts word-level romanized → Devanagari mappings from the existing
parallel datasets. Uses frequency ranking to keep only high-confidence pairs.

The output JSON is used by:
  - Python pipeline: `scripts/transliterator/fallback_map.py` (loaded at runtime)
  - JS browser:      `public/transliteration_map.json` (cached by Service Worker)

Usage:
  python scripts/build_transliteration_map.py

Output:
  public/transliteration_map.json
"""

import pandas as pd
import json
import re
import os
import sys
from collections import Counter

# ─────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────
DATA_DIR = os.path.join("datasets")
OUTPUT_PATH = os.path.join("public", "transliteration_map.json")
MIN_FREQUENCY = 3      # Minimum occurrences to include a mapping
MAX_MAP_SIZE = 10000    # Cap the map size for browser payload

# Devanagari Unicode range
DEVANAGARI_RE = re.compile(r'^[\u0900-\u097F\u0966-\u096F]+$')
# Basic Latin (romanized) — no digits, no special chars
ROMAN_RE = re.compile(r'^[a-zA-Z]+$')


def is_devanagari(text: str) -> bool:
    """Check if a string is pure Devanagari script."""
    return bool(DEVANAGARI_RE.match(text.strip()))


def is_romanized(text: str) -> bool:
    """Check if a string is pure Latin alphabet (potential romanized Marathi/Hindi)."""
    return bool(ROMAN_RE.match(text.strip()))


def extract_word_pairs_from_parallel(roman_col_data, deva_col_data):
    """
    Given parallel romanized and Devanagari sentence columns,
    extract word-level aligned pairs where the word counts match.

    Only keeps pairs where the sentence has the same number of tokens
    in both columns (naive word alignment).
    """
    pair_counter = Counter()
    aligned = 0
    skipped = 0

    for roman_sent, deva_sent in zip(roman_col_data, deva_col_data):
        if not isinstance(roman_sent, str) or not isinstance(deva_sent, str):
            skipped += 1
            continue

        roman_tokens = roman_sent.strip().split()
        deva_tokens = deva_sent.strip().split()

        # Only use sentences where word count matches (naive alignment)
        if len(roman_tokens) != len(deva_tokens):
            skipped += 1
            continue

        if len(roman_tokens) == 0:
            skipped += 1
            continue

        aligned += 1
        for r_tok, d_tok in zip(roman_tokens, deva_tokens):
            r_clean = r_tok.strip().lower()
            d_clean = d_tok.strip()

            # Only keep pairs where one side is romanized and the other is Devanagari
            if is_romanized(r_clean) and is_devanagari(d_clean):
                pair_counter[(r_clean, d_clean)] += 1

    return pair_counter, aligned, skipped


def detect_columns(df):
    """
    Auto-detect which columns contain romanized text and Devanagari text
    by sampling the first 100 rows.
    """
    roman_col = None
    deva_col = None

    for col in df.columns:
        sample = df[col].dropna().head(100).astype(str)
        roman_count = sum(1 for s in sample if any(is_romanized(w) for w in s.split()[:3]))
        deva_count = sum(1 for s in sample if any(is_devanagari(w) for w in s.split()[:3]))

        if deva_count > 50 and deva_col is None:
            deva_col = col
        elif roman_count > 50 and roman_col is None:
            roman_col = col

    return roman_col, deva_col


def process_parquet(filepath: str, pair_counter: Counter):
    """Process a single parquet file and add word pairs to the counter."""
    print(f"\n  Loading: {filepath}")

    try:
        df = pd.read_parquet(filepath)
    except Exception as e:
        print(f"  ❌ Error loading {filepath}: {e}")
        return 0, 0

    print(f"  Shape: {df.shape}")
    print(f"  Columns: {df.columns.tolist()}")

    # Auto-detect romanized and Devanagari columns
    roman_col, deva_col = detect_columns(df)

    if roman_col is None or deva_col is None:
        print(f"  ⚠️ Could not auto-detect romanized/Devanagari column pair.")
        print(f"     Detected: roman={roman_col}, deva={deva_col}")
        print(f"     Skipping this file.")
        return 0, 0

    print(f"  Romanized column: '{roman_col}'")
    print(f"  Devanagari column: '{deva_col}'")

    # Extract word pairs
    new_pairs, aligned, skipped = extract_word_pairs_from_parallel(
        df[roman_col], df[deva_col]
    )
    pair_counter.update(new_pairs)

    print(f"  Aligned sentences: {aligned:,}")
    print(f"  Skipped sentences: {skipped:,}")
    print(f"  Unique word pairs found: {len(new_pairs):,}")

    return aligned, skipped


def process_json_dictionaries(data_dir: str, pair_counter: Counter):
    """Process JSON dictionary files for additional mappings."""
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]

    for jf in json_files:
        filepath = os.path.join(data_dir, jf)
        print(f"\n  Loading JSON: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

        # JSON dictionaries have varied formats — try common patterns
        added = 0
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    # Try to find romanized→devanagari pairs
                    for key in ['marlish', 'hinglish', 'romanized', 'input']:
                        for val_key in ['marathi', 'hindi', 'devanagari', 'target']:
                            if key in entry and val_key in entry:
                                r = str(entry[key]).strip().lower()
                                d = str(entry[val_key]).strip()
                                if is_romanized(r) and is_devanagari(d):
                                    pair_counter[(r, d)] += 1
                                    added += 1

        print(f"  Added {added} pairs from {jf}")


def build_map(pair_counter: Counter, min_freq: int, max_size: int) -> dict:
    """
    Build the final transliteration map from frequency-counted pairs.

    For each romanized token, keeps only the most frequent Devanagari mapping.
    Filters by minimum frequency and caps total size.
    """
    # Group by romanized token, find the most frequent Devanagari for each
    roman_to_candidates = {}
    for (roman, deva), count in pair_counter.items():
        if count < min_freq:
            continue
        if roman not in roman_to_candidates or count > roman_to_candidates[roman][1]:
            roman_to_candidates[roman] = (deva, count)

    # Sort by frequency (highest first), cap at max_size
    sorted_pairs = sorted(
        roman_to_candidates.items(),
        key=lambda x: x[1][1],
        reverse=True
    )[:max_size]

    # Build the final map
    final_map = {roman: deva for roman, (deva, count) in sorted_pairs}

    return final_map


def main():
    print("=" * 60)
    print("  Build Transliteration Map from Datasets")
    print("=" * 60)

    pair_counter = Counter()
    total_aligned = 0
    total_skipped = 0

    # Process parquet files
    parquet_files = [
        os.path.join(DATA_DIR, "Marathi_part_1.parquet"),
        os.path.join(DATA_DIR, "Marathi_part_2.parquet"),
        os.path.join(DATA_DIR, "Hinglish_part_1.parquet"),
        os.path.join(DATA_DIR, "Hinglish_part_2.parquet"),
    ]

    for pf in parquet_files:
        if os.path.exists(pf):
            aligned, skipped = process_parquet(pf, pair_counter)
            total_aligned += aligned
            total_skipped += skipped
        else:
            print(f"\n  ⚠️ File not found: {pf}")

    # Process JSON dictionaries
    process_json_dictionaries(DATA_DIR, pair_counter)

    # Build final map
    print(f"\n{'='*60}")
    print(f"  Building final map...")
    print(f"  Total unique (roman, deva) pairs: {len(pair_counter):,}")
    print(f"  Total aligned sentences processed: {total_aligned:,}")
    print(f"  Min frequency threshold: {MIN_FREQUENCY}")
    print(f"  Max map size: {MAX_MAP_SIZE}")

    final_map = build_map(pair_counter, MIN_FREQUENCY, MAX_MAP_SIZE)

    print(f"  Final map size: {len(final_map):,} entries")

    # Save to JSON
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_map, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"\n  ✅ Saved to: {OUTPUT_PATH}")
    print(f"  File size: {file_size / 1024:.1f} KB")

    # Show top 20 entries
    print(f"\n  Top 20 most frequent mappings:")
    sorted_pairs = sorted(pair_counter.items(), key=lambda x: x[1], reverse=True)[:20]
    for (roman, deva), count in sorted_pairs:
        print(f"    {roman:15s} → {deva:15s}  (freq: {count:,})")

    print(f"\n{'='*60}")
    print(f"  Done! Map ready for use by transliteration pipeline.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
