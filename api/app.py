"""
Marlish.AI — Translation API

Multilingual translation supporting all Marlish.AI language pairs:
  - Marlish/Hinglish (romanized) → English
  - Pure Marathi/Hindi (Devanagari) → English
  - English → Marathi/Hindi (Devanagari)
  - Cross: Marlish ↔ Hinglish (via English pivot)

Uses NLLB-200-distilled-600M (200-language model) + custom transliteration pipeline.

Usage:
    uvicorn api.app:app --host 0.0.0.0 --port 8000

Endpoints:
    POST /translate  — translate text between any supported pair
    GET  /health     — liveness check
"""

import os
import sys
import time

# ─────────────────────────────────────────────────────────
# Add project root to path so we can import the transliterator
# ─────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from scripts.transliterator.pipeline import MarlishTransliterationPipeline
from scripts.transliterator.reverse_transliterate import reverse_transliterate
from scripts.transliterator.fallback_map import SEED_MAP


# ─────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────
MODEL_NAME = "facebook/nllb-200-1.3B"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Map frontend language codes → NLLB language codes
NLLB_LANG_MAP = {
    "english":  "eng_Latn",
    "hindi":    "hin_Deva",
    "marathi":  "mar_Deva",
    "hinglish": "hin_Deva",  # Transliterated to Hindi Devanagari first
    "marlish":  "mar_Deva",  # Transliterated to Marathi Devanagari first
}

# Languages that need transliteration (romanized → Devanagari) before NLLB
ROMANIZED_LANGS = {"hinglish", "marlish"}


# ─────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title="Marlish.AI Translation API",
    description="Multilingual translation for Indian languages using NLLB-200",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────
# Models (loaded once at startup)
# ─────────────────────────────────────────────────────────
transliterator: MarlishTransliterationPipeline = None
tokenizer = None
model = None


@app.on_event("startup")
async def load_models():
    global transliterator, tokenizer, model

    print(f"[Startup] Device: {DEVICE}")
    if DEVICE == "cuda":
        print(f"[Startup] GPU: {torch.cuda.get_device_name(0)}")

    # Load transliteration pipeline
    print("[Startup] Loading transliteration pipeline...")
    transliterator = MarlishTransliterationPipeline()
    print("[Startup] Transliteration pipeline ready.")

    # Load NLLB-200
    print(f"[Startup] Loading {MODEL_NAME}...")
    start = time.time()

    # Suppress download noise
    from transformers.utils import logging as hf_logging
    hf_logging.set_verbosity_error()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    dtype = torch.float16 if DEVICE == "cuda" else torch.float32
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        torch_dtype=dtype,
    ).to(DEVICE)

    load_time = time.time() - start
    print(f"[Startup] NLLB-200 loaded in {load_time:.1f}s on {DEVICE}")
    print("[Startup] API ready.")


# ─────────────────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────────────────
class TranslateRequest(BaseModel):
    text: str
    source: str = "marlish"
    target: str = "english"

class TranslateResponse(BaseModel):
    translation: str
    devanagari: Optional[str] = None  # Only set when transliteration was performed
    latency_ms: float


# ─────────────────────────────────────────────────────────
# Core translation logic
# ─────────────────────────────────────────────────────────
def do_nllb_translate(text: str, src_nllb: str, tgt_nllb: str) -> str:
    """Run NLLB-200 translation between any two supported languages."""
    tokenizer.src_lang = src_nllb
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
    ).to(DEVICE)

    tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_nllb)

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            forced_bos_token_id=tgt_lang_id,
            max_new_tokens=128,
        )

    return tokenizer.decode(generated[0], skip_special_tokens=True)


# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────
@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if model is None or tokenizer is None or transliterator is None:
        raise HTTPException(status_code=503, detail="Models not loaded yet")

    source = request.source.lower()
    target = request.target.lower()

    if source not in NLLB_LANG_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported source: {source}")
    if target not in NLLB_LANG_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported target: {target}")

    start = time.time()
    text = request.text.strip()
    devanagari = None

    # Step 1: If source is romanized (marlish/hinglish), transliterate to Devanagari
    if source in ROMANIZED_LANGS:
        devanagari = transliterator.transliterate(text)
        model_input = devanagari
    else:
        # Pure Devanagari or English — pass directly to NLLB
        model_input = text

    # Step 2: Translate using NLLB-200
    src_nllb = NLLB_LANG_MAP[source]
    tgt_nllb = NLLB_LANG_MAP[target]

    translation = do_nllb_translate(model_input, src_nllb, tgt_nllb)

    # Step 3: If target is romanized (marlish/hinglish), reverse-transliterate
    # NLLB outputs Devanagari → convert back to chat-style romanized text
    if target in ROMANIZED_LANGS:
        devanagari = translation  # Save the Devanagari form
        translation = reverse_transliterate(translation, SEED_MAP)

    latency = (time.time() - start) * 1000

    return TranslateResponse(
        translation=translation,
        devanagari=devanagari,
        latency_ms=round(latency, 2),
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "device": DEVICE,
        "ready": model is not None,
    }
