# Marlish.AI — Technology Stack

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Production

---

## Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Next.js** | 16.2 | React framework (App Router) |
| **React** | 19.2 | UI components |
| **Tailwind CSS** | v4 | Styling (utility-first) |
| **Lucide React** | 1.8 | Icon library |
| **PostHog** | 1.369 | Analytics (optional) |

## Backend (API)

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Runtime |
| **FastAPI** | 0.115+ | REST API framework |
| **Uvicorn** | 0.30+ | ASGI server |
| **PyTorch** | 2.2+ | ML framework (CPU or CUDA) |
| **Transformers** | 4.40-4.x | HuggingFace model loading |
| **SentencePiece** | 0.2+ | Tokenization (NLLB) |
| **google-genai** | 1.0+ | Gemini GEC API client |

## ML Models

| Model | Provider | Size | Purpose |
|-------|----------|------|---------|
| **NLLB-200-1.3B** | Meta | 2.5GB | Translation (200 languages) |
| **Gemini 2.5-flash-lite** | Google | API | Grammar correction (English) |

## Infrastructure

| Service | Tier | Purpose |
|---------|------|---------|
| **Vercel** | Free | Frontend hosting (bom1/Mumbai) |
| **HF Spaces** | Free (CPU) | API hosting (Docker) |
| **GitHub** | Free | Source control |
| **Gemini API** | Free | GEC (15 RPM, 1M tokens/day) |

## Development Tools

| Tool | Purpose |
|------|---------|
| **Vitest** | JavaScript testing |
| **pip/venv** | Python package management |
| **Docker** | Container builds for HF Spaces |

## Key Constraints

- `transformers` must be `<5.0.0` (5.x breaks compatibility with torch 2.12)
- CPU inference: 15-30s per translation (free tier)
- GPU inference: 1-2s per translation (requires T4 or better)
- NLLB model downloads ~2.5GB on first start
