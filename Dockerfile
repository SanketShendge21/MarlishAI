# MarlishAI Translation API — Hugging Face Spaces Docker (Free Tier / CPU)
#
# Runs on HF Spaces free tier (CPU, 16GB RAM).
# NLLB-200-1.3B runs on CPU — slower (~15-30s/request) but free.
# Upgrade to T4 GPU ($0.60/hr) for real-time speed (~1-2s/request).
#
# Build: docker build -t marlishai-api .
# Run:   docker run -p 7860:7860 marlishai-api

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

EXPOSE 7860

USER user

# Start the API
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "7860"]
