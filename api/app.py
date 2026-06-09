"""
Marlish.AI — Translation API

Multilingual translation supporting all Marlish.AI language pairs:
  - Marlish/Hinglish (romanized) → English
  - Pure Marathi/Hindi (Devanagari) → English
  - English → Marathi/Hindi (Devanagari)
  - Cross: Marlish ↔ Hinglish (via English pivot)

Uses NLLB-200-1.3B + custom transliteration pipeline.
Optional: Gemini 2.5-flash-lite GEC post-processing for natural English output.

Usage:
    GEMINI_API_KEY=xxx uvicorn api.app:app --host 0.0.0.0 --port 8000

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

# Optional: Gemini GEC post-processing
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("[Warning] google-genai not installed. GEC post-processing disabled.")
    print("  Install with: pip install google-genai")


# ─────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────
MODEL_NAME = "facebook/nllb-200-1.3B"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load API key from .local.env or environment
def _load_env_key(key_name: str) -> str:
    """Load a key from .local.env file, falling back to os.environ."""
    env_path = os.path.join(PROJECT_ROOT, ".local.env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(key_name):
                        # Parse: key = "value" or key=value
                        _, _, val = line.partition("=")
                        return val.strip().strip('"').strip("'")
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "")

GEMINI_API_KEY = _load_env_key("Marlish_Gemini_API_Key")
GEC_ENABLED = bool(GEMINI_API_KEY) and GENAI_AVAILABLE

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
    allow_origins=[
        "http://localhost:3000",             # Local Next.js dev
        "http://localhost:8000",             # Local API (Swagger docs)
        "https://marlishai.vercel.app",      # Vercel production
        "https://marlish-ai.vercel.app",     # Vercel alt domain
        "https://*.vercel.app",              # Vercel preview deploys
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # All Vercel preview URLs
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
gemini_client = None


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

    # Load Gemini GEC client (optional)
    global gemini_client
    if GEC_ENABLED:
        try:
            gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            print("[Startup] Gemini GEC enabled (gemini-2.5-flash-lite)")
        except Exception as e:
            print(f"[Startup] Gemini GEC failed to initialize: {e}")
            gemini_client = None
    else:
        if not GEMINI_API_KEY:
            print("[Startup] Gemini GEC disabled (no GEMINI_API_KEY set)")
        print("[Startup] Translation will use raw NLLB output (no post-processing)")

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


def refine_with_gec(nmt_output: str, source_lang: str, target_lang: str) -> str:
    """
    Use Gemini 2.5-flash-lite to refine NLLB's raw output into natural text.
    Only applied when target is English (GEC for Devanagari output isn't needed).
    Falls back to raw output on any error.
    """
    if not gemini_client or target_lang != "english":
        return nmt_output

    prompt = (
        "You are a grammar correction assistant. Fix the grammar and make this "
        "sound like natural conversational English. Do NOT add any new information, "
        "do NOT explain, do NOT add filler words. Just return the corrected sentence. "
        "If the sentence is already correct, return it unchanged.\n\n"
        f"Sentence: {nmt_output}"
    )

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        refined = response.text.strip()
        # Sanity check: if Gemini returns something wildly different or empty, use original
        if refined and len(refined) < len(nmt_output) * 3:
            return refined
        return nmt_output
    except Exception as e:
        print(f"[GEC] Gemini error: {e}")
        return nmt_output


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

    # Step 2b: GEC post-processing (only for English output)
    if target == "english" and gemini_client:
        translation = refine_with_gec(translation, source, target)

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
        "gec_enabled": gemini_client is not None,
    }
