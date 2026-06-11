---
title: Marlish.AI Custom ML/NLP Model Roadmap
date: 2026-05-03
---

# Marlish.AI — Custom ML/NLP Model Roadmap

## 1. Data Preparation

- **a. Data Extraction & Cleaning**
  - Parse `apni_bhasha_100k_training_dataset.csv` for Hinglish/Marlish ↔ English sentence pairs.
  - Remove duplicates, empty, or malformed rows.
  - Normalize text (lowercase, remove extra spaces, apply typo-map normalization if needed).

- **b. Data Splitting**
  - Split into train/validation/test sets (e.g., 80/10/10).

- **c. Optional Augmentation**
  - Expand with typo variants, slang, and abbreviations using typo-map and variants from your JSON datasets.

---

## 2. Model Selection & Training

- **a. Model Choice**
  - Use a lightweight seq2seq model: `T5-small`, `mT5-small`, or `MarianMT`.
  - For browser/offline use, prioritize models with ONNX/Transformers.js compatibility.

- **b. Training Pipeline**
  - Use HuggingFace Transformers (PyTorch or TensorFlow).
  - Tokenize sentence pairs.
  - Fine-tune the model on your parallel data.
  - Monitor BLEU/ROUGE scores on validation set.

- **c. Export & Quantization**
  - Export the trained model to ONNX.
  - Quantize to INT8 for size/performance (target <40MB).

---

## 3. Integration with Marlish.AI Pipeline

- **a. ML Fallback Logic**
  - Add a confidence threshold in your JS pipeline (dictionary-engine.js).
  - If rule-based output confidence < threshold, call the ML model.

- **b. Browser Inference**
  - Use Transformers.js or ONNX.js for in-browser inference.
  - Load the quantized model alongside your dictionary.

- **c. Preprocessing**
  - Always run typo normalization and grammar reordering before ML inference.

---

## 4. Testing & Evaluation

- **a. Automated Tests**
  - Create test cases for known hard/ambiguous sentences.
  - Compare outputs: dictionary-only vs. hybrid vs. ML-only.

- **b. User Feedback Loop**
  - Log corrections and user edits for future self-learning.

---

## 5. Deployment & Optimization

- **a. Bundle Model Efficiently**
  - Lazy-load the ML model only when needed.
  - Cache in IndexedDB for offline use.

- **b. Monitor Performance**
  - Track latency, memory, and accuracy in real-world usage.

---

## 6. Documentation & Maintenance

- **a. Document the Hybrid Flow**
  - Update docs to explain the hybrid pipeline and fallback logic.

- **b. Plan for Continuous Data Expansion**
  - Add new sentence pairs and slang as you collect more data.

---

## 🚦 Next Steps

1. Write a data preprocessing script (Python) to extract, clean, and split your parallel corpus.
2. Set up a HuggingFace training script for T5-small or MarianMT.
3. Train and export the model.
4. Integrate the model into your JS pipeline as a fallback.
5. Test and optimize.

---

This plan is tailored for Marlish.AI’s hybrid architecture and leverages your unique Hinglish/Marlish datasets for maximum impact.