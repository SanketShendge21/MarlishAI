"""
Marlish.AI — Export Model to ONNX Format
Step 2c in the ML/NLP Model Roadmap:
  - Export the fine-tuned mT5 model to ONNX format
  - Quantize to INT8 for browser deployment (<40MB target)
  
Requirements:
  pip install optimum[onnxruntime] onnx onnxruntime
"""
import os
import sys
from pathlib import Path

# --- CONFIG ---
MODEL_DIR = os.path.join('models', 'marlish_mt5_finetuned')
ONNX_OUTPUT_DIR = os.path.join('models', 'marlish_mt5_onnx')
QUANTIZED_OUTPUT_DIR = os.path.join('models', 'marlish_mt5_quantized')


def export_to_onnx():
    """Export the PyTorch model to ONNX format using Optimum."""
    from optimum.onnxruntime import ORTModelForSeq2SeqLM

    print("📦 Exporting model to ONNX...")
    os.makedirs(ONNX_OUTPUT_DIR, exist_ok=True)

    # Export using Optimum (library_name needed for local fine-tuned models)
    model = ORTModelForSeq2SeqLM.from_pretrained(
        MODEL_DIR,
        export=True,
        library_name="transformers",
    )
    model.save_pretrained(ONNX_OUTPUT_DIR)

    # Also copy tokenizer
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(ONNX_OUTPUT_DIR)

    print(f"  ✅ ONNX model saved to: {ONNX_OUTPUT_DIR}")

    # Calculate size
    total_size = sum(f.stat().st_size for f in Path(ONNX_OUTPUT_DIR).rglob('*') if f.is_file())
    print(f"  Model size: {total_size / 1e6:.1f} MB")

    return ONNX_OUTPUT_DIR


def quantize_model(onnx_dir):
    """Quantize the ONNX model to INT8 for reduced size and faster inference."""
    from optimum.onnxruntime import ORTQuantizer
    from optimum.onnxruntime.configuration import AutoQuantizationConfig

    print("\n🔧 Quantizing model to INT8...")
    os.makedirs(QUANTIZED_OUTPUT_DIR, exist_ok=True)

    # Set up quantization config
    qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)

    # Create quantizer for encoder and decoder
    model = ORTModelForSeq2SeqLM.from_pretrained(onnx_dir)

    encoder_quantizer = ORTQuantizer.from_pretrained(onnx_dir, file_name="encoder_model.onnx")
    decoder_quantizer = ORTQuantizer.from_pretrained(onnx_dir, file_name="decoder_model.onnx")

    encoder_quantizer.quantize(save_dir=QUANTIZED_OUTPUT_DIR, quantization_config=qconfig)
    decoder_quantizer.quantize(save_dir=QUANTIZED_OUTPUT_DIR, quantization_config=qconfig)

    # Copy tokenizer
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(onnx_dir)
    tokenizer.save_pretrained(QUANTIZED_OUTPUT_DIR)

    # Calculate size
    total_size = sum(f.stat().st_size for f in Path(QUANTIZED_OUTPUT_DIR).rglob('*') if f.is_file())
    print(f"  ✅ Quantized model saved to: {QUANTIZED_OUTPUT_DIR}")
    print(f"  Quantized size: {total_size / 1e6:.1f} MB")

    return QUANTIZED_OUTPUT_DIR


def main():
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print("=" * 60)
    print("  Marlish.AI — ONNX Export & Quantization")
    print("=" * 60)

    if not os.path.exists(MODEL_DIR):
        print(f"\n❌ Model not found at {MODEL_DIR}")
        print("  Please run train_model.py first!")
        return

    # Step 1: Export to ONNX
    onnx_dir = export_to_onnx()

    # Step 2: Quantize
    try:
        quantized_dir = quantize_model(onnx_dir)
        print(f"\n🎉 Export & quantization complete!")
        print(f"  Use the quantized model at: {quantized_dir}")
    except Exception as e:
        print(f"\n⚠️  Quantization failed: {e}")
        print(f"  You can still use the non-quantized ONNX model at: {onnx_dir}")


if __name__ == '__main__':
    main()
