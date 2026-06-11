"""Minimal IndicTrans2 load test — writes all output to a log file."""
import sys
import os
import traceback
import io

# Redirect ALL output to a log file
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "IT2_TEST_OUTPUT.txt")
log_file = open(LOG_PATH, "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Step 1: Importing torch...", flush=True)
    import torch
    print(f"  torch: {torch.__version__}, CUDA: {torch.cuda.is_available()}", flush=True)

    print("Step 2: Importing transformers...", flush=True)
    import transformers
    print(f"  transformers: {transformers.__version__}", flush=True)

    print("Step 3: Importing AutoTokenizer, AutoModelForSeq2SeqLM...", flush=True)
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    print("  OK", flush=True)

    print("Step 4: Loading IndicProcessor...", flush=True)
    from scripts.indic_processor import IndicProcessor
    ip = IndicProcessor(inference=True)
    print("  OK", flush=True)

    print("Step 5: Loading tokenizer for indictrans2-indic-en-dist-200M...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(
        "ai4bharat/indictrans2-indic-en-dist-200M", trust_remote_code=True
    )
    print(f"  OK, vocab size: {tokenizer.vocab_size}", flush=True)

    print("Step 6: Loading model...", flush=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForSeq2SeqLM.from_pretrained(
        "ai4bharat/indictrans2-indic-en-dist-200M",
        trust_remote_code=True,
        torch_dtype=dtype,
    ).to(device)
    print(f"  OK, loaded on {device}", flush=True)

    print("Step 7: Test translation...", flush=True)
    src_lang = "mar_Deva"
    tgt_lang = "eng_Latn"
    test_text = "कसा आहेस मित्रा"

    batch = ip.preprocess_batch([test_text], src_lang=src_lang, tgt_lang=tgt_lang)
    print(f"  Preprocessed: {batch}", flush=True)

    inputs = tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(device)

    with torch.no_grad():
        generated = model.generate(**inputs, num_beams=5, max_new_tokens=128)

    decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
    result = ip.postprocess_batch(decoded, lang=tgt_lang)[0]

    print(f"  Input:  {test_text}", flush=True)
    print(f"  Output: {result}", flush=True)
    print("\n=== SUCCESS: IndicTrans2 works! ===", flush=True)

except Exception as e:
    print(f"\n=== FAILED ===", flush=True)
    print(f"Error type: {type(e).__name__}", flush=True)
    print(f"Error: {e}", flush=True)
    traceback.print_exc(file=log_file)
    log_file.flush()
    log_file.close()
    sys.exit(1)

log_file.flush()
log_file.close()
