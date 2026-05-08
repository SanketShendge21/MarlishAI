import pandas as pd
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import os

# 1. Configuration
parquet_files = ['Marathi_part_1.parquet', 'Marathi_part_2.parquet']
output_csv = 'Apni_Bhasha_Marlish_Dataset.csv'

def convert_to_marlish(text):
    try:
        # Safety check for empty rows
        if not isinstance(text, str):
            return text
            
        # Converts Devanagari to formal Roman IAST
        roman_text = transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)
        
        # Clean up the accents to make it casual chat "Marlish"
        replacements = {
            'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṭ': 't', 
            'ḍ': 'd', 'ṇ': 'n', 'ś': 'sh', 'ṣ': 'sh', 'ṃ': 'm', 
            'ḥ': 'h', 'ē': 'e', 'ō': 'o'
        }
        for char, replacement in replacements.items():
            roman_text = roman_text.replace(char, replacement)
        
        return roman_text.lower()
    except Exception:
        return text

# 2. Process Files Sequentially
for index, file in enumerate(parquet_files):
    print(f"\n🚀 Loading {file}...")
    
    if not os.path.exists(file):
        print(f"❌ Error: Could not find {file} in this folder.")
        continue

    # Read the parquet file
    df = pd.read_parquet(file)
    
    # 3. Format Data for Apni Bhasha
    # Rename 'src' and 'tgt' to our target column names
    df = df.rename(columns={'src': 'english', 'tgt': 'marathi_devanagari'})
    
    # Drop the 'idx' column to save space (not needed for training)
    if 'idx' in df.columns:
        df = df.drop(columns=['idx'])

    print(f"⚙️ Transliterating Marathi Devanagari to Marlish... (Grab a coffee, this takes a few minutes)")
    
    # Apply the conversion logic
    df['marlish'] = df['marathi_devanagari'].apply(convert_to_marlish)

    # Reorder the columns so they look clean in the CSV
    df = df[['marlish', 'marathi_devanagari', 'english']]

    # 4. Save to CSV
    print(f"💾 Saving processed data...")
    if index == 0:
        # For the first file, write the header
        df.to_csv(output_csv, index=False)
    else:
        # For the second file, append without repeating the header
        df.to_csv(output_csv, mode='a', header=False, index=False)

    print(f"✅ Finished processing {file}!")

print(f"\n🎉 ALL DONE! Your custom Marlish dataset is saved as: {output_csv}")