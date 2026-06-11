# MarlishAI Translation API — Hugging Face Spaces Docker
# GPU Runtime: T4 (16GB VRAM) — enough for NLLB-200-1.3B
#
# Build: docker build -t marlishai-api .
# Run:   docker run --gpus all -p 7860:7860 marlishai-api

FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app user (HF Spaces requirement)
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Install Python deps first (cache layer)
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy API code
COPY api/ ./api/
COPY scripts/transliterator/ ./scripts/transliterator/

# Copy .local.env if it exists (for API keys) — will be overridden by HF Secrets
COPY .local.env* ./

# HF Spaces expects port 7860
ENV PORT=7860
ENV PYTHONIOENCODING=utf-8
# Set via HF Spaces Secrets:
# ENV GEMINI_API_KEY=xxx

EXPOSE 7860

# Start the API
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "7860"]
