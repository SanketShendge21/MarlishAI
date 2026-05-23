"""
Marlish.AI — Model Evaluation Script
Step 4 in the ML/NLP Model Roadmap:
  - Evaluate trained model on test set
  - Compare dictionary-only vs ML outputs
  - Generate sample translations for review
  
Requirements:
  pip install torch transformers sentencepiece evaluate sacrebleu
"""
import os
import sys
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import evaluate

# --- CONFIG ---
DATA_DIR = os.path.join('docs', 'Dictionary_Refs', 'ml_splits')
MODEL_DIR = os.path.join('models', 'marlish_mt5_finetuned')
NUM_SAMPLES = 50  # Number of sample translations to show


def translate_batch(model, tokenizer, texts, direction, device, max_length=128):
    """Translate a batch of texts using the trained model."""
    # Dynamically construct prefix from direction string
    parts = direction.split('_to_')
    if len(parts) == 2:
        src_lang = parts[0].capitalize()
        tgt_lang = parts[1].capitalize()
        prefix = f'translate {src_lang} to {tgt_lang}: '
    else:
        prefix = 'translate to English: '
    prefixed = [prefix + t for t in texts]

    inputs = tokenizer(prefixed, return_tensors="pt", padding=True, truncation=True, max_length=max_length).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=4,
            early_stopping=True,
        )

    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return decoded


def main():
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print("=" * 60)
    print("  Marlish.AI — Model Evaluation")
    print("=" * 60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n🖥️  Device: {device}")

    # Load model
    print(f"\n🤖 Loading model from {MODEL_DIR}...")
    if not os.path.exists(MODEL_DIR):
        print(f"❌ Model not found! Run train_model.py first.")
        return

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR).to(device)
    model.eval()

    # Load test data
    print(f"\n📥 Loading test data...")
    test_df = pd.read_csv(os.path.join(DATA_DIR, 'test.csv'), encoding='utf-8')
    print(f"  Test set: {len(test_df):,} pairs")

    # Evaluate BLEU score
    print(f"\n📊 Computing BLEU scores by direction...")
    metric = evaluate.load("sacrebleu")

    for direction in test_df['direction'].unique():
        subset = test_df[test_df['direction'] == direction].head(1000)
        if len(subset) == 0:
            continue

        predictions = []
        references = []

        # Process in batches
        batch_size = 16
        for i in range(0, len(subset), batch_size):
            batch = subset.iloc[i:i+batch_size]
            sources = batch['source'].tolist()
            targets = batch['target'].tolist()

            preds = translate_batch(model, tokenizer, sources, direction, device)
            predictions.extend(preds)
            references.extend([[t] for t in targets])

        result = metric.compute(predictions=predictions, references=references)
        print(f"  {direction}: BLEU = {result['score']:.2f} (on {len(subset)} samples)")

    # Show sample translations
    print(f"\n🔍 Sample translations ({NUM_SAMPLES} examples):")
    print("-" * 80)

    samples = test_df.sample(n=min(NUM_SAMPLES, len(test_df)), random_state=42)
    for _, row in samples.iterrows():
        source = str(row['source'])
        target = str(row['target'])
        direction = str(row['direction'])

        pred = translate_batch(model, tokenizer, [source], direction, device)[0]

        print(f"  Direction: {direction}")
        print(f"  Source:    {source[:100]}")
        print(f"  Expected:  {target[:100]}")
        print(f"  Model:     {pred[:100]}")
        print(f"  {'✅' if pred.strip().lower() == target.strip().lower() else '❌'}")
        print()

    print("🎉 Evaluation complete!")


if __name__ == '__main__':
    main()
