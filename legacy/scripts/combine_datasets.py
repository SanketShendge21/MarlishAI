import os
import pandas as pd
import json
import re

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

# --- Find all Parquet files in the data directory ---
def find_parquet_files():
    return [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.parquet')]
OUTPUT_CSV = os.path.join(DATA_DIR, 'Combined_Parallel_Dataset.csv')

COLUMNS = ['Hindi', 'Hinglish', 'Marathi', 'Marlish', 'English']

def normalize(text):
    if not isinstance(text, str):
        return ''
    return re.sub(r'\s+', ' ', text.strip())

def parse_csvs():
    rows = []
    for fname in CSV_FILES:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            print(f"[WARN] File not found: {fname}")
            continue
        df = pd.read_csv(path)
        # Try to map columns to standard names
        col_map = {c.lower(): c for c in df.columns}
        for _, row in df.iterrows():
            rows.append({
                'Hindi': normalize(row.get(col_map.get('hindi_devanagari', ''))),
                'Hinglish': normalize(row.get(col_map.get('hinglish', ''))),
                'Marathi': normalize(row.get(col_map.get('marathi_devanagari', ''))),
                'Marlish': normalize(row.get(col_map.get('marlish', ''))),
                'English': normalize(row.get(col_map.get('english', ''))),
            })
    return rows

# --- Parse all Parquet files in the data directory ---
def parse_parquets():
    rows = []
    parquet_files = find_parquet_files()
    for fname in parquet_files:
        path = os.path.join(DATA_DIR, fname)
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            print(f"[WARN] Could not read parquet {fname}: {e}")
            continue
        cols = [c.lower() for c in df.columns]
        if 'input' in cols and 'output' in cols:
            # Hinglish parquet
            for _, row in df.iterrows():
                rows.append({
                    'Hindi': normalize(row.get('input_devanagari', '')),
                    'Hinglish': normalize(row.get('input', '')),
                    'Marathi': '',
                    'Marlish': '',
                    'English': normalize(row.get('output', '')),
                })
        elif 'src' in cols and 'tgt' in cols:
            # Marathi parquet
            for _, row in df.iterrows():
                rows.append({
                    'Hindi': '',
                    'Hinglish': '',
                    'Marathi': normalize(row.get('src', '')),
                    'Marlish': '',
                    'English': normalize(row.get('tgt', '')),
                })
        else:
            print(f"[WARN] Unknown parquet structure in {fname}, skipping.")
    return rows

def parse_jsons():
    rows = []
    for fname in JSON_FILES:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            print(f"[WARN] File not found: {fname}")
            continue
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Try to find the main list (usually under 'hinglish' or top-level list)
        if isinstance(data, dict):
            # Try 'hinglish', 'marlish', or all values
            for key in ['hinglish', 'marlish']:
                if key in data and isinstance(data[key], list):
                    entries = data[key]
                    for entry in entries:
                        rows.append({
                            'Hindi': '',
                            'Hinglish': normalize(entry.get('word', '')) if key == 'hinglish' else '',
                            'Marathi': '',
                            'Marlish': normalize(entry.get('word', '')) if key == 'marlish' else '',
                            'English': normalize(entry.get('meaning_en', '')),
                        })
            # If no 'hinglish' or 'marlish', try all values
            if not rows:
                for v in data.values():
                    if isinstance(v, list):
                        for entry in v:
                            rows.append({
                                'Hindi': '',
                                'Hinglish': normalize(entry.get('word', '')),
                                'Marathi': '',
                                'Marlish': '',
                                'English': normalize(entry.get('meaning_en', '')),
                            })
        elif isinstance(data, list):
            for entry in data:
                rows.append({
                    'Hindi': '',
                    'Hinglish': normalize(entry.get('word', '')),
                    'Marathi': '',
                    'Marlish': '',
                    'English': normalize(entry.get('meaning_en', '')),
                })
    return rows

def deduplicate(rows):
    def norm(val):
        return re.sub(r'\s+', ' ', str(val).strip().lower()) if val else ''
    seen = set()
    unique = []
    for row in rows:
        key = tuple(norm(row.get(col, '')) for col in COLUMNS)
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def main():
    print("Parsing CSVs...")
    rows = parse_csvs()
    print(f"Rows from CSVs: {len(rows)}")
    print("Parsing Parquet files...")
    rows += parse_parquets()
    print(f"Rows after adding Parquet: {len(rows)}")
    print("Parsing JSONs...")
    rows += parse_jsons()
    print(f"Total rows before deduplication: {len(rows)}")
    rows = deduplicate(rows)
    print(f"Total rows after deduplication: {len(rows)}")
    df = pd.DataFrame(rows, columns=COLUMNS)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Combined dataset saved to {OUTPUT_CSV}")

if __name__ == '__main__':
    main()