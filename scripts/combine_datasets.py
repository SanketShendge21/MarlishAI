"""
Marlish.AI — Combined Parallel Dataset Builder (Optimized)
Merges ALL data sources: CSVs, JSONs, Parquets + adds Devanagari alphabet mappings.
Uses vectorized pandas operations for speed with large datasets.
"""
import os
import pandas as pd
import json
import re
import sys

# --- CONFIG ---
DATA_DIR = os.path.join('docs', 'Dictionary_Refs')
CSV_FILES = [
    'apni_bhasha_100k_training_dataset.csv',
    'Apni_Bhasha_Dataset.csv',
    'Apni_Bhasha_Marlish_Dataset.csv',
]
JSON_FILES = [
    'hinglish_marlish_10000_dataset.json',
    'hinglish_marlish_v2_25000_dataset.json',
    'hinglish_marlish_v3_production_100k.json',
    'marlish_ai_5000_premium_dataset.json',
]
OUTPUT_CSV = os.path.join(DATA_DIR, 'Combined_Parallel_Dataset.csv')
COLUMNS = ['Hindi', 'Hinglish', 'Marathi', 'Marlish', 'English']


def normalize_series(s):
    """Vectorized text normalization for a pandas Series."""
    return s.fillna('').astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)


# --- Hindi (Devanagari) alphabet mapping to English ---
def get_hindi_alphabet_rows():
    vowels = [
        ('अ', 'a', 'A'), ('आ', 'aa', 'Aa'), ('इ', 'i', 'I'), ('ई', 'ee', 'Ee'),
        ('उ', 'u', 'U'), ('ऊ', 'oo', 'Oo'), ('ऋ', 'ri', 'Ri'),
        ('ए', 'e', 'E'), ('ऐ', 'ai', 'Ai'), ('ओ', 'o', 'O'), ('औ', 'au', 'Au'),
        ('अं', 'an', 'An'), ('अः', 'ah', 'Ah'),
    ]
    consonants = [
        ('क', 'ka', 'Ka'), ('ख', 'kha', 'Kha'), ('ग', 'ga', 'Ga'), ('घ', 'gha', 'Gha'), ('ङ', 'nga', 'Nga'),
        ('च', 'cha', 'Cha'), ('छ', 'chha', 'Chha'), ('ज', 'ja', 'Ja'), ('झ', 'jha', 'Jha'), ('ञ', 'nya', 'Nya'),
        ('ट', 'ta', 'Ta'), ('ठ', 'tha', 'Tha'), ('ड', 'da', 'Da'), ('ढ', 'dha', 'Dha'), ('ण', 'na', 'Na'),
        ('त', 'ta', 'Ta'), ('थ', 'tha', 'Tha'), ('द', 'da', 'Da'), ('ध', 'dha', 'Dha'), ('न', 'na', 'Na'),
        ('प', 'pa', 'Pa'), ('फ', 'pha', 'Pha'), ('ब', 'ba', 'Ba'), ('भ', 'bha', 'Bha'), ('म', 'ma', 'Ma'),
        ('य', 'ya', 'Ya'), ('र', 'ra', 'Ra'), ('ल', 'la', 'La'), ('व', 'va', 'Va'),
        ('श', 'sha', 'Sha'), ('ष', 'sha', 'Sha'), ('स', 'sa', 'Sa'), ('ह', 'ha', 'Ha'),
        ('क्ष', 'ksha', 'Ksha'), ('त्र', 'tra', 'Tra'), ('ज्ञ', 'gya', 'Gya'),
    ]
    numbers = [
        ('०', '0', 'Zero'), ('१', '1', 'One'), ('२', '2', 'Two'), ('३', '3', 'Three'),
        ('४', '4', 'Four'), ('५', '5', 'Five'), ('६', '6', 'Six'), ('७', '7', 'Seven'),
        ('८', '8', 'Eight'), ('९', '9', 'Nine'),
    ]
    rows = []
    for dev, hinglish, eng in vowels + consonants + numbers:
        rows.append({'Hindi': dev, 'Hinglish': hinglish, 'Marathi': '', 'Marlish': '', 'English': eng})
    return pd.DataFrame(rows, columns=COLUMNS)


# --- Marathi (Devanagari) alphabet mapping to English ---
def get_marathi_alphabet_rows():
    vowels = [
        ('अ', 'a', 'A'), ('आ', 'aa', 'Aa'), ('इ', 'i', 'I'), ('ई', 'ee', 'Ee'),
        ('उ', 'u', 'U'), ('ऊ', 'oo', 'Oo'), ('ऋ', 'ru', 'Ru'),
        ('ए', 'e', 'E'), ('ऐ', 'ai', 'Ai'), ('ओ', 'o', 'O'), ('औ', 'au', 'Au'),
        ('अं', 'an', 'An'), ('अः', 'ah', 'Ah'),
    ]
    consonants = [
        ('क', 'ka', 'Ka'), ('ख', 'kha', 'Kha'), ('ग', 'ga', 'Ga'), ('घ', 'gha', 'Gha'), ('ङ', 'nga', 'Nga'),
        ('च', 'cha', 'Cha'), ('छ', 'chha', 'Chha'), ('ज', 'ja', 'Ja'), ('झ', 'jha', 'Jha'), ('ञ', 'nya', 'Nya'),
        ('ट', 'ta', 'Ta'), ('ठ', 'tha', 'Tha'), ('ड', 'da', 'Da'), ('ढ', 'dha', 'Dha'), ('ण', 'na', 'Na'),
        ('त', 'ta', 'Ta'), ('थ', 'tha', 'Tha'), ('द', 'da', 'Da'), ('ध', 'dha', 'Dha'), ('न', 'na', 'Na'),
        ('प', 'pa', 'Pa'), ('फ', 'pha', 'Pha'), ('ब', 'ba', 'Ba'), ('भ', 'bha', 'Bha'), ('म', 'ma', 'Ma'),
        ('य', 'ya', 'Ya'), ('र', 'ra', 'Ra'), ('ल', 'la', 'La'), ('व', 'va', 'Va'),
        ('श', 'sha', 'Sha'), ('ष', 'sha', 'Sha'), ('स', 'sa', 'Sa'), ('ह', 'ha', 'Ha'),
        ('ळ', 'la', 'La'),  # Marathi-specific
        ('क्ष', 'ksha', 'Ksha'), ('ज्ञ', 'dnya', 'Dnya'),  # ज्ञ = 'dnya' in Marathi
    ]
    numbers = [
        ('०', '0', 'Zero'), ('१', '1', 'One'), ('२', '2', 'Two'), ('३', '3', 'Three'),
        ('४', '4', 'Four'), ('५', '5', 'Five'), ('६', '6', 'Six'), ('७', '7', 'Seven'),
        ('८', '8', 'Eight'), ('९', '9', 'Nine'),
    ]
    rows = []
    for dev, marlish, eng in vowels + consonants + numbers:
        rows.append({'Hindi': '', 'Hinglish': '', 'Marathi': dev, 'Marlish': marlish, 'English': eng})
    return pd.DataFrame(rows, columns=COLUMNS)


def parse_csvs():
    """Parse CSV files using vectorized pandas operations."""
    frames = []
    for fname in CSV_FILES:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            print(f"  [WARN] File not found: {fname}")
            continue
        print(f"  Loading CSV: {fname}...", flush=True)
        try:
            df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
        except Exception:
            df = pd.read_csv(path, encoding='latin-1', on_bad_lines='skip')

        # Case-insensitive column mapping
        col_map = {c.lower(): c for c in df.columns}

        result = pd.DataFrame()
        result['Hindi'] = normalize_series(df.get(col_map.get('hindi_devanagari', col_map.get('hindi', '')), pd.Series(dtype=str)))
        result['Hinglish'] = normalize_series(df.get(col_map.get('hinglish', ''), pd.Series(dtype=str)))
        result['Marathi'] = normalize_series(df.get(col_map.get('marathi_devanagari', col_map.get('marathi', '')), pd.Series(dtype=str)))
        result['Marlish'] = normalize_series(df.get(col_map.get('marlish', ''), pd.Series(dtype=str)))
        result['English'] = normalize_series(df.get(col_map.get('english', ''), pd.Series(dtype=str)))

        frames.append(result)
        print(f"    → {len(result)} rows from {fname}")

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS)


def parse_parquets():
    """Parse ALL parquet files — Hinglish AND Marathi — vectorized."""
    frames = []
    parquet_files = sorted([f for f in os.listdir(DATA_DIR) if f.lower().endswith('.parquet')])

    if not parquet_files:
        print("  [WARN] No parquet files found.")
        return pd.DataFrame(columns=COLUMNS)

    for fname in parquet_files:
        path = os.path.join(DATA_DIR, fname)
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            print(f"  [WARN] Could not read {fname}: {e}")
            continue

        cols_lower = [c.lower() for c in df.columns]
        print(f"  Loading Parquet: {fname} ({len(df):,} rows)...", flush=True)

        if 'input' in cols_lower and 'output' in cols_lower:
            # ====== Hinglish parquet ======
            result = pd.DataFrame()
            result['Hindi'] = normalize_series(df.get('input_devanagari', pd.Series(dtype=str)))
            result['Hinglish'] = normalize_series(df.get('input', pd.Series(dtype=str)))
            result['Marathi'] = ''
            result['Marlish'] = ''
            result['English'] = normalize_series(df.get('output', pd.Series(dtype=str)))
            frames.append(result)
            print(f"    → {len(result):,} Hinglish rows from {fname}")

        elif 'src' in cols_lower and 'tgt' in cols_lower:
            # ====== Marathi parquet ======
            result = pd.DataFrame()
            result['Hindi'] = ''
            result['Hinglish'] = ''
            result['Marathi'] = normalize_series(df.get('src', pd.Series(dtype=str)))
            result['Marlish'] = ''
            result['English'] = normalize_series(df.get('tgt', pd.Series(dtype=str)))
            frames.append(result)
            print(f"    → {len(result):,} Marathi rows from {fname}")
        else:
            print(f"  [WARN] Unknown structure in {fname}: {df.columns.tolist()}")

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS)


def parse_jsons():
    """Parse JSON dictionary files."""
    rows = []
    for fname in JSON_FILES:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            print(f"  [WARN] File not found: {fname}")
            continue
        print(f"  Loading JSON: {fname}...", flush=True)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        if isinstance(data, dict):
            for key in ['hinglish', 'marlish']:
                if key in data and isinstance(data[key], list):
                    for entry in data[key]:
                        word = re.sub(r'\s+', ' ', str(entry.get('word', '')).strip())
                        meaning = re.sub(r'\s+', ' ', str(entry.get('meaning_en', '')).strip())
                        rows.append({
                            'Hindi': '',
                            'Hinglish': word if key == 'hinglish' else '',
                            'Marathi': '',
                            'Marlish': word if key == 'marlish' else '',
                            'English': meaning,
                        })
                        count += 1
            if count == 0:
                for v in data.values():
                    if isinstance(v, list):
                        for entry in v:
                            word = re.sub(r'\s+', ' ', str(entry.get('word', '')).strip())
                            meaning = re.sub(r'\s+', ' ', str(entry.get('meaning_en', '')).strip())
                            rows.append({
                                'Hindi': '', 'Hinglish': word, 'Marathi': '', 'Marlish': '', 'English': meaning,
                            })
                            count += 1
        elif isinstance(data, list):
            for entry in data:
                word = re.sub(r'\s+', ' ', str(entry.get('word', '')).strip())
                meaning = re.sub(r'\s+', ' ', str(entry.get('meaning_en', '')).strip())
                rows.append({
                    'Hindi': '', 'Hinglish': word, 'Marathi': '', 'Marlish': '', 'English': meaning,
                })
                count += 1
        print(f"    → {count} rows from {fname}")

    return pd.DataFrame(rows, columns=COLUMNS) if rows else pd.DataFrame(columns=COLUMNS)


def main():
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print("=" * 60)
    print("  Marlish.AI — Combined Parallel Dataset Builder")
    print("=" * 60)

    frames = []

    # 1. Parse CSVs
    print("\n📄 Step 1: Parsing CSV files...")
    csv_df = parse_csvs()
    frames.append(csv_df)
    print(f"  Total from CSVs: {len(csv_df):,}")

    # 2. Parse JSONs
    print("\n📦 Step 2: Parsing JSON files...")
    json_df = parse_jsons()
    frames.append(json_df)
    print(f"  Total from JSONs: {len(json_df):,}")

    # 3. Parse Parquets (Hinglish + Marathi)
    print("\n🗃️  Step 3: Parsing Parquet files (Hinglish + Marathi)...")
    parquet_df = parse_parquets()
    frames.append(parquet_df)
    print(f"  Total from Parquets: {len(parquet_df):,}")

    # 4. Add Hindi (Devanagari) alphabet mappings
    print("\n🔤 Step 4: Adding Hindi (Devanagari) alphabet mappings...")
    hindi_alpha_df = get_hindi_alphabet_rows()
    frames.append(hindi_alpha_df)
    print(f"  Added {len(hindi_alpha_df)} Hindi alphabet rows")

    # 5. Add Marathi (Devanagari) alphabet mappings
    print("\n🔤 Step 5: Adding Marathi (Devanagari) alphabet mappings...")
    marathi_alpha_df = get_marathi_alphabet_rows()
    frames.append(marathi_alpha_df)
    print(f"  Added {len(marathi_alpha_df)} Marathi alphabet rows")

    # 6. Combine all
    print("\n🔗 Step 6: Combining all data...")
    combined = pd.concat(frames, ignore_index=True)
    combined = combined[COLUMNS]  # Ensure column order
    combined = combined.fillna('')
    print(f"  Total combined rows: {len(combined):,}")

    # 7. Deduplicate
    print("\n🔁 Step 7: Deduplicating...")
    before = len(combined)
    dedup_key = combined.apply(lambda row: tuple(str(row[c]).strip().lower() for c in COLUMNS), axis=1)
    combined = combined[~dedup_key.duplicated(keep='first')]
    combined = combined.reset_index(drop=True)
    print(f"  Before: {before:,} → After: {len(combined):,} (removed {before - len(combined):,} duplicates)")

    # 8. Save
    print(f"\n💾 Step 8: Saving to {OUTPUT_CSV}...")
    combined.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    print(f"  ✅ Saved {len(combined):,} rows")

    # Summary
    print("\n📊 Summary:")
    for col in COLUMNS:
        count = (combined[col].replace('', pd.NA).dropna()).shape[0]
        print(f"  {col:>10}: {count:>10,} non-empty rows")
    print(f"\n🎉 Done!")


if __name__ == '__main__':
    main()