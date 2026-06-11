"""
Marlish.AI — Data Preprocessing Script for ML Training
Step 1 in the ML/NLP Model Roadmap:
  - Extract and clean parallel corpus from Combined_Parallel_Dataset.csv
  - Split into train/validation/test sets (80/10/10)
  - Save to docs/Dictionary_Refs/ml_splits/
"""
import os
import sys
import pandas as pd
import re
from sklearn.model_selection import train_test_split

# --- CONFIG ---
DATA_DIR = os.path.join('docs', 'Dictionary_Refs')
INPUT_CSV = os.path.join(DATA_DIR, 'Combined_Parallel_Dataset.csv')
OUTPUT_DIR = os.path.join(DATA_DIR, 'ml_splits')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# We train on Hinglish → English (primary) and Marlish → English (secondary)
# Rows must have at least one source language and English translation
MIN_TEXT_LEN = 2
MAX_TEXT_LEN = 512


def clean_text(text):
    """Normalize a text string for ML training."""
    if not isinstance(text, str):
        return ''
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    # Remove excessive punctuation
    text = re.sub(r'([.!?])\1+', r'\1', text)
    return text


def main():
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print("=" * 60)
    print("  Marlish.AI — ML Data Preprocessing Pipeline")
    print("=" * 60)

    import gc

    # 1. Load the combined dataset (with dtype=str to save memory and avoid DtypeWarnings)
    print(f"\n📥 Loading {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV, dtype=str, encoding='utf-8')
    print(f"  Total rows loaded: {len(df):,}")

    # Clean English right away
    df['English'] = df['English'].fillna('').apply(clean_text)

    # 3. Create parallel pairs for training dynamically
    print("\n🔗 Creating parallel training pairs (memory optimized)...")
    pairs = []

    langs = [('Hinglish', 'hinglish'), ('Marlish', 'marlish'), ('Hindi', 'hindi'), ('Marathi', 'marathi')]
    
    for col, prefix in langs:
        # Clean current language
        df[col] = df[col].fillna('').apply(clean_text)
        
        # Filter valid lengths directly
        mask = (
            (df[col].str.len() >= MIN_TEXT_LEN) & (df[col].str.len() <= MAX_TEXT_LEN) &
            (df['English'].str.len() >= MIN_TEXT_LEN) & (df['English'].str.len() <= MAX_TEXT_LEN)
        )
        subset = df[mask]
        
        # X -> English
        x_to_e = subset[[col, 'English']].copy()
        x_to_e.columns = ['source', 'target']
        x_to_e['direction'] = f'{prefix}_to_english'
        x_to_e = x_to_e.drop_duplicates(subset=['source', 'target'])
        pairs.append(x_to_e)
        
        # English -> X
        e_to_x = subset[['English', col]].copy()
        e_to_x.columns = ['source', 'target']
        e_to_x['direction'] = f'english_to_{prefix}'
        e_to_x = e_to_x.drop_duplicates(subset=['source', 'target'])
        pairs.append(e_to_x)
        
        print(f"  {col} ↔ English: {len(x_to_e) * 2:,} pairs")
        
        # Free memory!
        df.drop(columns=[col], inplace=True)
        gc.collect()

    # Free the main dataframe completely
    del df
    gc.collect()

    print("\n📦 Concatenating all language pairs...")
    all_pairs = pd.concat(pairs, ignore_index=True)
    
    # Final global deduplication
    before = len(all_pairs)
    all_pairs = all_pairs.drop_duplicates(subset=['source', 'target']).reset_index(drop=True)
    print(f"  Total pairs after dedup: {len(all_pairs):,} (removed {before - len(all_pairs):,})")

    # 4. Split into train/val/test (80/10/10)
    print("\n✂️  Splitting into train/val/test (80/10/10)...")
    train_df, temp_df = train_test_split(all_pairs, test_size=0.2, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

    print(f"  Train: {len(train_df):,}")
    print(f"  Val:   {len(val_df):,}")
    print(f"  Test:  {len(test_df):,}")

    # 5. Save splits
    print(f"\n💾 Saving to {OUTPUT_DIR}/...")
    train_df.to_csv(os.path.join(OUTPUT_DIR, 'train.csv'), index=False, encoding='utf-8')
    val_df.to_csv(os.path.join(OUTPUT_DIR, 'val.csv'), index=False, encoding='utf-8')
    test_df.to_csv(os.path.join(OUTPUT_DIR, 'test.csv'), index=False, encoding='utf-8')

    # 6. Print summary by direction
    print("\n📊 Distribution by direction:")
    for split_name, split_df in [('Train', train_df), ('Val', val_df), ('Test', test_df)]:
        print(f"\n  {split_name}:")
        for direction, count in split_df['direction'].value_counts().items():
            print(f"    {direction}: {count:,}")

    print(f"\n🎉 Data preprocessing complete!")


if __name__ == '__main__':
    main()
