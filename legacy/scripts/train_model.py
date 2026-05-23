"""
Marlish.AI — Model Training Script (GPU-Optimized)
Step 2 in the ML/NLP Model Roadmap:
  - Fine-tune mT5-small on bidirectional parallel corpus (8 directions)
  - Uses google/mt5-small (~300M params, multilingual Seq2Seq)
  - Optimized for GPU training with FP16 mixed precision on RTX 3060
  
Requirements:
  pip install torch transformers sentencepiece datasets evaluate sacrebleu accelerate>=1.1.0
"""
import os
import sys
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq,
)
import evaluate
import numpy as np
import time
import torch
torch.cuda.empty_cache()

# --- CONFIG ---
DATA_DIR = os.path.join('docs', 'Dictionary_Refs', 'ml_splits')
MODEL_NAME = "google/mt5-small"  # Powerful multilingual seq2seq model (GPU recommended)
OUTPUT_DIR = os.path.join('models', 'marlish_mt5_finetuned')
MAX_SOURCE_LEN = 128
MAX_TARGET_LEN = 128
BATCH_SIZE = 32      # Maximizes GPU utilization on 12GB RTX 3060 with bf16. If OOM, fall back to 16.
EPOCHS = 3
LEARNING_RATE = 3e-5
WARMUP_STEPS = 500
EVAL_STEPS = 5000     # Evaluate BLEU every 5000 steps 
SAVE_STEPS = 5000     # Checkpoint every 5000 steps (resumable) also should be in multiple of EVAL_STEPS for best model saving to work correctly
LOGGING_STEPS = 500
GRAD_ACCUM_STEPS = 1  # No accumulation needed — batch 32 fits in VRAM
MAX_TRAIN_SAMPLES = 500000    # Recommended: 500k subset for initial full-pipeline validation
MAX_EVAL_SAMPLES = 5000


class TranslationDataset(Dataset):
    """Custom dataset for parallel translation pairs."""

    def __init__(self, dataframe, tokenizer, max_source_len, max_target_len, direction_prefix=True):
        self.data = dataframe.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_source_len = max_source_len
        self.max_target_len = max_target_len
        self.direction_prefix = direction_prefix

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        source = str(row['source'])
        target = str(row['target'])
        direction = str(row.get('direction', ''))

        # Add direction prefix for multi-task learning dynamically
        if self.direction_prefix and direction:
            parts = direction.split('_to_')
            if len(parts) == 2:
                src_lang = parts[0].capitalize()
                tgt_lang = parts[1].capitalize()
                prefix = f'translate {src_lang} to {tgt_lang}: '
            else:
                prefix = 'translate to English: '
            source = prefix + source

        # Tokenize source (return numpy arrays for fast batching)
        source_encoding = self.tokenizer(
            source,
            max_length=self.max_source_len,
            truncation=True,
            padding='max_length',
        )

        # Tokenize target
        target_encoding = self.tokenizer(
            text_target=target,
            max_length=self.max_target_len,
            truncation=True,
            padding='max_length',
        )

        labels = target_encoding['input_ids'].copy()
        labels = [l if l != self.tokenizer.pad_token_id else -100 for l in labels]

        return {
            'input_ids': source_encoding['input_ids'],
            'attention_mask': source_encoding['attention_mask'],
            'labels': labels,
        }


def compute_metrics(eval_preds, tokenizer, metric):
    """Compute BLEU score for evaluation."""
    preds, labels = eval_preds

    if isinstance(preds, tuple):
        preds = preds[0]

    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    decoded_preds = [pred.strip() for pred in decoded_preds]
    decoded_labels = [[label.strip()] for label in decoded_labels]

    result = metric.compute(predictions=decoded_preds, references=decoded_labels)
    return {"bleu": result["score"]}


def main():
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print("=" * 60)
    print("  Marlish.AI — Model Training Pipeline (GPU-Optimized)")
    print("=" * 60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n🖥️  Device: {device}")

    # 1. Load data
    print(f"\n📥 Loading training data from {DATA_DIR}/...")
    train_df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'), encoding='utf-8')
    val_df = pd.read_csv(os.path.join(DATA_DIR, 'val.csv'), encoding='utf-8')
    test_df = pd.read_csv(os.path.join(DATA_DIR, 'test.csv'), encoding='utf-8')

    print(f"  Full Train: {len(train_df):,} pairs")
    print(f"  Full Val:   {len(val_df):,} pairs")
    print(f"  Full Test:  {len(test_df):,} pairs")

    # Limit samples — sample balanced across directions
    if MAX_TRAIN_SAMPLES:
        num_directions = train_df['direction'].nunique()
        per_dir = MAX_TRAIN_SAMPLES // num_directions
        sampled_parts = []
        for direction in train_df['direction'].unique():
            subset = train_df[train_df['direction'] == direction]
            sampled_parts.append(subset.sample(n=min(per_dir, len(subset)), random_state=42))
        train_df = pd.concat(sampled_parts, ignore_index=True)
        print(f"  → Sampled train to {len(train_df):,} (balanced across directions)")
    if MAX_EVAL_SAMPLES:
        val_df = val_df.sample(n=min(MAX_EVAL_SAMPLES, len(val_df)), random_state=42).reset_index(drop=True)
        print(f"  → Sampled val to {len(val_df):,}")

    # Print distribution
    print("\n  Train distribution:")
    for d, c in train_df['direction'].value_counts().items():
        print(f"    {d}: {c:,}")

    # 2. Load tokenizer and model
    print(f"\n🤖 Loading model: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    param_count = sum(p.numel() for p in model.parameters())
    print(f"  Model parameters: {param_count:,} ({param_count/1e6:.0f}M)")
    print(f"  Vocab size: {tokenizer.vocab_size:,}")

    # 3. Create datasets
    print("\n📦 Creating datasets...")
    train_dataset = TranslationDataset(train_df, tokenizer, MAX_SOURCE_LEN, MAX_TARGET_LEN)
    val_dataset = TranslationDataset(val_df, tokenizer, MAX_SOURCE_LEN, MAX_TARGET_LEN)

    total_steps = (len(train_dataset) // BATCH_SIZE) * EPOCHS
    print(f"  Train samples: {len(train_dataset):,}")
    print(f"  Val samples: {len(val_dataset):,}")
    print(f"  Total training steps: {total_steps:,}")
    est_time = total_steps * 1.5  # ~1.5s per step on CPU for MarianMT
    print(f"  Estimated training time: ~{est_time/60:.0f} minutes")

    # 4. Set up metrics
    metric = evaluate.load("sacrebleu")

    # 5. Training arguments
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    training_args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        learning_rate=LEARNING_RATE,
        warmup_steps=WARMUP_STEPS,
        weight_decay=0.01,
        eval_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_steps=SAVE_STEPS,
        save_total_limit=3,
        logging_steps=LOGGING_STEPS,
        predict_with_generate=True,
        generation_max_length=MAX_TARGET_LEN,
        # CRITICAL: mT5 requires bf16, NOT fp16!
        # mT5 was pre-trained with bfloat16. Using fp16 causes loss=0 and grad_norm=NaN
        # because mT5's internal activations overflow float16's narrow range (max ~65,504).
        # RTX 3060 (Ampere, Compute Capability 8.6) natively supports bf16.
        fp16=False,
        bf16=torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8,
        report_to="none",
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        greater_is_better=True,
        optim="adamw_torch",
        dataloader_num_workers=4,   # Parallel data loading (CPU prepares next batch while GPU trains)
        dataloader_pin_memory=True,  # Fast CPU→GPU DMA transfer for NVIDIA GPUs
    )

    # 6. Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
    )

    # 7. Trainer
    print("\n🏋️ Starting training...")
    start_time = time.time()

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=lambda preds: compute_metrics(preds, tokenizer, metric),
    )

    # Check for existing checkpoints to resume from
    last_checkpoint = None
    if os.path.isdir(OUTPUT_DIR):
        checkpoints = [d for d in os.listdir(OUTPUT_DIR) if d.startswith("checkpoint-")]
        if checkpoints:
            last_checkpoint = True  # Tell trainer to find the latest
            print("  [INFO] Found existing checkpoints. Training will resume from where it left off!")

    # Train
    train_result = trainer.train(resume_from_checkpoint=last_checkpoint)
    elapsed = time.time() - start_time

    # 8. Save final model
    print(f"\n💾 Saving model to {OUTPUT_DIR}...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # 9. Log metrics
    print("\n📊 Training Results:")
    print(f"  Train loss: {train_result.training_loss:.4f}")
    print(f"  Train time: {elapsed:.0f}s ({elapsed/60:.1f} min)")

    # 10. Evaluate on test set
    print("\n🧪 Evaluating on test set...")
    test_sample = test_df.sample(n=min(500, len(test_df)), random_state=42)
    test_dataset = TranslationDataset(test_sample, tokenizer, MAX_SOURCE_LEN, MAX_TARGET_LEN)
    test_results = trainer.evaluate(eval_dataset=test_dataset)
    print(f"  Test BLEU: {test_results.get('eval_bleu', 'N/A')}")
    print(f"  Test Loss: {test_results.get('eval_loss', 'N/A'):.4f}")

    # 11. Show sample translations
    print("\n🔍 Sample translations:")
    print("-" * 60)
    samples = test_sample.head(10)
    model.eval()
    for _, row in samples.iterrows():
        source = str(row['source'])
        target = str(row['target'])
        direction = str(row['direction'])

        parts = direction.split('_to_')
        if len(parts) == 2:
            src_lang = parts[0].capitalize()
            tgt_lang = parts[1].capitalize()
            prefix = f'translate {src_lang} to {tgt_lang}: '
        else:
            prefix = 'translate to English: '
        inputs = tokenizer(prefix + source, return_tensors="pt", max_length=MAX_SOURCE_LEN, truncation=True).to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=MAX_TARGET_LEN, num_beams=4)
        pred = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(f"  [{direction}]")
        print(f"  Source:   {source[:80]}")
        print(f"  Expected: {target[:80]}")
        print(f"  Model:    {pred[:80]}")
        match = "✅" if pred.strip().lower() == target.strip().lower() else "❌"
        print(f"  {match}")
        print()

    print(f"\n🎉 Training complete! Model saved to: {OUTPUT_DIR}")
    print("  Next steps:")
    print("  1. Run scripts/export_onnx.py to export to ONNX format")
    print("  2. Integrate with the JS pipeline as fallback")


if __name__ == '__main__':
    main()
