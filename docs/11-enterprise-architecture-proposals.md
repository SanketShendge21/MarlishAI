# Marlish.AI — Enterprise Architecture Considerations

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Reference (for future scaling)
>
> **NOTE:** These are considerations for when the application needs to scale beyond free tier. Not implemented in v1.0.

---

## Current Architecture (v1.0 — Free Tier)

| Component | Technology | Limitation |
|-----------|-----------|------------|
| Frontend | Vercel (free) | 100GB bandwidth/month |
| API | HF Spaces Docker (free CPU) | 15-30s latency, auto-sleep |
| Translation | NLLB-200-1.3B | CPU-bound on free tier |
| GEC | Gemini free tier | 15 RPM, 1M tokens/day |

## Scaling Path

### Stage 1: Production Speed (Budget: ~₹1500/month)
- Upgrade HF Spaces to **T4 GPU** → 1-2s latency
- Add **Redis caching** (Vercel KV free tier) → cache frequent translations
- Expected: handles ~100 concurrent users

### Stage 2: High Availability (Budget: ~₹5000/month)
- Deploy API on **Railway.app** or **Render** with GPU
- Add **load balancer** for multiple API instances
- **CDN** for static frontend assets (already via Vercel)
- **Uptime monitoring** (Better Uptime free tier)
- Expected: handles ~1000 concurrent users

### Stage 3: Enterprise (Budget: ~₹25000/month)
- Deploy on **AWS/GCP** with auto-scaling GPU instances
- **API gateway** (Kong/AWS API Gateway) for rate limiting, auth
- **Kubernetes** for container orchestration
- **CI/CD** pipeline (GitHub Actions → auto-deploy)
- **Multi-region** deployment for low latency globally
- **User accounts** with translation history sync
- Expected: handles ~10000+ concurrent users

## Technologies Worth Integrating (Future)

| Technology | When | Why |
|-----------|------|-----|
| **Redis/Vercel KV** | Stage 1 | Cache frequent translations (80% of queries are repeats) |
| **Cloudflare Tunnel** | Now | Expose local GPU to internet for free |
| **GitHub Actions** | Stage 1 | Auto-deploy on push |
| **PostHog** | Already integrated | Usage analytics |
| **Sentry** | Stage 1 | Error tracking |
| **Docker Compose** | Stage 2 | Local multi-container dev |
| **Kubernetes** | Stage 3 | Production orchestration |
| **WebSocket** | Stage 2 | Streaming translation output |

## Technologies NOT Worth Integrating

| Technology | Why Not |
|-----------|---------|
| **Kafka/RabbitMQ** | Overkill — translation is request/response, not event-driven |
| **GraphQL** | Simple REST API is sufficient for 2 endpoints |
| **Microservices** | Monolith API is fine at this scale |
| **Blockchain** | No use case |
| **Custom training pipeline** | NLLB works well enough; fine-tuning via QLoRA is simpler |

## Security Considerations

| Concern | Current Mitigation |
|---------|-------------------|
| API key exposure | `.local.env` + `.gitignore` |
| CORS | Restricted to Vercel domains |
| User data | No server-side storage |
| Rate limiting | Gemini has built-in limits; add API-level limits at Stage 2 |
| DDoS | Vercel has built-in protection; HF Spaces has basic limits |