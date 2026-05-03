# Marlish.AI — Deployment Guide

> **Version:** 2.0 | **Date:** 2026-04-19 | **Status:** Updated (Open-Source First)

---

## 1. Deployment Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTION STACK                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CLOUDFLARE (CDN + WAF)                  │   │
│  │  - Global CDN for static assets                      │   │
│  │  - Rate Limiting on Tier 3 API (100K/day free)       │   │
│  │  - Bot Management + DDoS protection                  │   │
│  │  - SSL/TLS termination                               │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              VERCEL (Hosting)                        │   │
│  │                                                      │   │
│  │  Static Assets ──► Vercel Edge Network (30+ PoPs)    │   │
│  │  Next.js PPR ──► Instant static shell + streaming    │   │
│  │  Tier 3 API ──► Edge Function (fallback route)       │   │
│  │                                                      │   │
│  │  CI/CD: GitHub push → auto-deploy (< 60s)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CLIENT-SIDE AI (No Server Needed)       │   │
│  │                                                      │   │
│  │  Tier 1: Aksharamukha.js (transliteration, < 1MB)    │   │
│  │  Tier 2: Transformers.js v4 + NLLB-200 (WebGPU)      │   │
│  │  Cache:  IndexedDB (translations + model weights)    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              TIER 3 FALLBACK (Edge/Server)           │   │
│  │                                                      │   │
│  │  Supabase: PostgreSQL + Auth + Edge Functions        │   │
│  │  Models:   IndicTrans3 / Gemma 3 4B (via HF API)     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MONITORING (Optional)                   │   │
│  │                                                      │   │
│  │  Analytics: PostHog (free tier, 1M events/mo)        │   │
│  │  Uptime:    Vercel built-in + BetterStack (free)     │   │
│  │  Errors:    Vercel Logs + Sentry (free tier)         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Environment Setup

### 2.1 Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20 LTS or 22 LTS | Runtime |
| npm / pnpm | Latest | Package manager (pnpm recommended for speed) |
| Git | Latest | Version control |
| Vercel CLI | Latest | Deployment + local dev |
| GitHub account | — | Repository + CI/CD |

### 2.2 Environment Variables

Create a `.env.local` file for local development (NEVER commit this):

```bash
# Supabase (for Tier 3 fallback + user data)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Hugging Face (for Tier 3 model inference - optional)
HF_API_TOKEN=your_huggingface_token

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_DAILY=500

# Feature Flags
ENABLE_TIER3_FALLBACK=true
NLLB_MODEL_ID=Xenova/nllb-200-distilled-600M

# Analytics (optional)
NEXT_PUBLIC_POSTHOG_KEY=your_posthog_key
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

For production, set these in Vercel Dashboard → Settings → Environment Variables.

**Note:** Unlike the previous cloud API approach, no LLM API keys (Gemini/OpenAI) are required for the core translation flow. The primary translation engine (NLLB-200) runs entirely in the browser.

---

## 3. Local Development

### 3.1 Initial Setup

```bash
# Clone the repository
git clone https://github.com/your-username/marlish-ai.git
cd marlish-ai

# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env.local
# Edit .env.local with your API keys

# Run development server
pnpm dev
# App available at http://localhost:3000
```

### 3.2 Local Testing Checklist

Before deploying, verify:

- [ ] All 5 translation pairs work correctly
- [ ] Debounce fires after 250ms of inactivity
- [ ] AbortController cancels stale requests (type fast, check network tab)
- [ ] SSE streaming renders tokens progressively
- [ ] Copy button works + shows checkmark animation
- [ ] TTS speaks in correct language voice
- [ ] Dark/Light mode toggle works + persists
- [ ] Input clear (X) button works
- [ ] Swap button works for valid pairs, disabled for invalid
- [ ] Rate limiting blocks after threshold (test with rapid requests)
- [ ] Mobile responsiveness (use Chrome DevTools mobile emulation)
- [ ] Lighthouse score > 90 (run `npx lighthouse http://localhost:3000`)

---

## 4. Deployment to Vercel

### 4.1 First-Time Setup

```bash
# Install Vercel CLI globally
npm i -g vercel

# Login to Vercel
vercel login

# Link project (from project root)
vercel link

# Set up environment variables on Vercel
vercel env add GEMINI_API_KEY production
vercel env add OPENAI_API_KEY production

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### 4.2 GitHub CI/CD (Recommended)

1. Push code to GitHub repository
2. Connect GitHub repo in Vercel Dashboard → New Project
3. Vercel auto-detects Next.js framework
4. Configure:
   - **Framework Preset:** Next.js
   - **Build Command:** `pnpm build` (or `npm run build`)
   - **Output Directory:** `.next`
   - **Install Command:** `pnpm install`
5. Add environment variables in Vercel Dashboard
6. Every `git push` to `main` triggers production deployment
7. Every PR creates a preview deployment with unique URL

### 4.3 Vercel Project Configuration

Create `vercel.json` in project root:

```json
{
  "framework": "nextjs",
  "regions": ["bom1"],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-store" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(self)" }
      ]
    }
  ]
}
```

**Note:** `"regions": ["bom1"]` deploys Edge Functions to Mumbai, India — closest to our target users. Vercel automatically serves static assets from the nearest global PoP regardless of this setting.

---

## 5. Vercel KV Setup (Edge Cache)

### 5.1 Create KV Store

1. Go to Vercel Dashboard → Storage → Create Database
2. Select **KV (Redis)** → Create
3. Link to your project
4. Environment variables (`KV_REST_API_URL`, `KV_REST_API_TOKEN`) are auto-populated

### 5.2 Usage in Edge Functions

```javascript
// Example: api/translate/route.js
import { kv } from '@vercel/kv';

export const runtime = 'edge';

export async function POST(request) {
  const { text, source, target } = await request.json();
  
  // Generate cache key
  const cacheKey = `translate:${source}:${target}:${normalize(text)}`;
  
  // Check cache
  const cached = await kv.get(cacheKey);
  if (cached) {
    return new Response(cached, { 
      headers: { 'X-Cache': 'HIT' } 
    });
  }
  
  // ... call LLM, stream response ...
  
  // Cache the result (TTL: 24 hours)
  await kv.set(cacheKey, fullResponse, { ex: 86400 });
}
```

### 5.3 KV Pricing (Vercel)

| Plan | Requests/month | Storage | Cost |
|------|---------------|---------|------|
| Hobby (Free) | 30,000 | 256 MB | $0 |
| Pro | 100,000 | 1 GB | Included in $20/mo |
| Enterprise | Unlimited | Custom | Custom |

---

## 6. Cloudflare Setup (CDN + WAF)

### 6.1 DNS Configuration

1. Register domain (e.g., `marlishai.com`) on any registrar
2. Add site to Cloudflare (free plan)
3. Update nameservers to Cloudflare
4. Add DNS records:
   ```
   Type: CNAME
   Name: @
   Target: cname.vercel-dns.com
   Proxy: Enabled (orange cloud)
   
   Type: CNAME
   Name: www
   Target: cname.vercel-dns.com
   Proxy: Enabled (orange cloud)
   ```
5. In Vercel: Add custom domain in Project Settings → Domains

### 6.2 Cloudflare Security Rules

```
Rule 1: Rate Limit API
├── URI Path: /api/translate
├── Action: Block
├── Threshold: 60 requests per minute per IP
└── Response: 429 Too Many Requests

Rule 2: Block Known Bots
├── Bot Score: < 30
├── Action: Managed Challenge
└── Applies to: All paths

Rule 3: Country Block (optional)
├── Block traffic from countries with no target users
├── Allow: IN, US, GB, AE, SG, CA, AU
└── Action: Block (or managed challenge)
```

### 6.3 Cloudflare Page Rules

```
Rule 1: Cache Static Assets
├── URL: marlishai.com/*.js, *.css, *.png, *.webp
├── Cache Level: Cache Everything
└── Edge Cache TTL: 1 month

Rule 2: Bypass Cache for API
├── URL: marlishai.com/api/*
├── Cache Level: Bypass
└── (API responses should never be CDN-cached at Cloudflare level)
```

---

## 7. Tier 3 Fallback Setup

### 7.1 Supabase (Database + Edge Functions)

1. Go to [Supabase](https://supabase.com/) → Create new project
2. Copy project URL and anon key to env vars
3. Create tables for:
   - `translation_history` (user translations)
   - `feedback` (thumbs up/down + corrections)
4. Deploy Edge Functions for Tier 3 translation:
   ```bash
   supabase functions deploy translate
   ```
5. Free tier includes: 500MB database, 50K MAU auth, 500K edge invocations

### 7.2 Hugging Face Inference API (IndicTrans3)

1. Go to [Hugging Face](https://huggingface.co/) → Create account
2. Generate API token → copy to `HF_API_TOKEN`
3. Use the Inference API to call IndicTrans3:
   ```javascript
   const response = await fetch(
     'https://api-inference.huggingface.co/models/ai4bharat/IndicTrans3-beta',
     {
       method: 'POST',
       headers: { 'Authorization': `Bearer ${HF_API_TOKEN}` },
       body: JSON.stringify({ inputs: text, parameters: { src_lang, tgt_lang } })
     }
   );
   ```
4. Free tier: rate-limited but sufficient for Tier 3 fallback volume

### 7.3 No Billing Caps Needed

Unlike the previous cloud API approach, there is **no risk of Denial of Wallet** for the core translation flow since it runs in-browser. Tier 3 uses free-tier services with built-in limits.

---

## 8. Monitoring & Observability

### 8.1 Vercel Analytics (Built-in)

- **Web Vitals:** FCP, LCP, CLS, INP tracked automatically
- **Function Logs:** All Edge Function executions logged (14-day retention)
- **Deployment History:** Full rollback capability

### 8.2 PostHog Analytics (Optional, Free Tier)

Track custom events:

```javascript
// Events to track
posthog.capture('translation_requested', {
  source_language: 'hinglish',
  target_language: 'en',
  input_length: text.length,
  cache_hit: false,
  latency_ms: 150
});

posthog.capture('translation_copied', { ... });
posthog.capture('translation_shared_whatsapp', { ... });
posthog.capture('tts_played', { language: 'mr' });
posthog.capture('theme_toggled', { theme: 'dark' });
```

### 8.3 Error Tracking (Sentry — Optional)

```bash
pnpm add @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

Free tier: 5,000 errors/month — more than sufficient for MVP.

---

## 9. Deployment Checklist

### Pre-Launch

- [ ] Supabase project created and env vars configured
- [ ] Hugging Face API token configured (for Tier 3)
- [ ] NLLB-200 model accessible from Hugging Face Hub
- [ ] Custom domain configured (DNS propagated)
- [ ] Cloudflare SSL mode set to "Full (Strict)"
- [ ] Cloudflare rate limiting rules active
- [ ] HTTPS redirect enabled
- [ ] `robots.txt` and `sitemap.xml` present
- [ ] Meta tags (title, description, OG) configured
- [ ] Favicon and PWA icons in place
- [ ] Lighthouse audit: Performance > 90, Accessibility > 90

### Post-Launch (Day 1-7)

- [ ] Monitor Vercel function logs for errors
- [ ] Monitor LLM API usage dashboards
- [ ] Verify rate limiting is working (test with curl loop)
- [ ] Check Cloudflare analytics for bot traffic
- [ ] Verify edge cache hit rate (target: 30%+)
- [ ] Run translations for all 5 language pairs
- [ ] Test on real mobile devices (Android Chrome, iOS Safari)
- [ ] Monitor PostHog for user behavior patterns

---

## 10. Cost Summary

### Monthly Running Costs (Estimated — Open-Source Stack)

| Service | Plan | Monthly Cost | Notes |
|---------|------|-------------|-------|
| **Vercel** | Hobby (free) | $0 | Free for personal projects |
| **Cloudflare** | Free plan | $0 | CDN + WAF + 100K Workers/day |
| **Supabase** | Free tier | $0 | 500MB DB, 50K MAU, 500K edge invocations |
| **Hugging Face** | Free tier | $0 | Rate-limited inference API |
| **NLLB-200 model** | Client-side | $0 | Runs in browser, cached in IndexedDB |
| **Aksharamukha.js** | Client-side | $0 | Runs in browser, < 1MB |
| **Domain** | Annual | ~$1/month | .com domain |
| **PostHog** | Free tier | $0 | 1M events/month |
| **Sentry** | Free tier | $0 | 5K errors/month |
| | | | |
| **TOTAL** | | **$0 — $1/month** | For 0 — 10K DAU |

**Comparison with previous cloud API stack:** $6-42/month → **$0-1/month** (96%+ cost reduction)

---

## 11. Scaling Triggers

| When this happens... | Do this... |
|---------------------|-----------|
| Tier 2 (NLLB-200) accuracy insufficient | Add Gemini Flash-Lite / GPT-4o-mini as commercial Tier 3 |
| DAU exceeds 10,000 | Upgrade Supabase to Pro ($25/mo) |
| Tier 3 edge invocations exceed free tier | Add Cloudflare Workers for routing |
| NLLB-200 download too slow on 3G | Implement chunked download with resume capability |
| DAU exceeds 50,000 | Fine-tune Gemma 3 with LoRA, export to ONNX for browser |
| Error rate > 1% | Investigate with Sentry, add circuit breaker on Tier 3 |

---

## 12. Rollback Strategy

Vercel supports instant rollbacks:

```bash
# List recent deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-url]

# Or use Vercel Dashboard:
# Deployments → Click previous deployment → "Promote to Production"
```

**Zero-downtime:** Vercel deployments are atomic. Old version serves until new version is fully ready.

---

## 13. Security Hardening Checklist

- [ ] Supabase service role key in environment variables (never in client)
- [ ] `.env.local` in `.gitignore`
- [ ] Content Security Policy (CSP) headers configured
- [ ] X-Frame-Options: DENY
- [ ] CORS restricted to own domain
- [ ] Input length validation (max 500 chars)
- [ ] Output length validation (max 3x input) for Tier 3
- [ ] Rate limiting active on Cloudflare for Tier 3 API
- [ ] No paid API keys required for core flow (client-side)
- [ ] No sensitive data logged (user input is NOT logged)
- [ ] Privacy disclaimer visible on the UI
- [ ] NLLB-200 model weights loaded from trusted source (Hugging Face Hub)
