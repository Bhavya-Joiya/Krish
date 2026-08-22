# Smart Crop Bot — Tech Stack

**Hackathon MVP (Zero-Cost)**  
Version 2.1 · August 22, 2026 · Everything free-tier capable

---

## 1. Stack Overview

This is the aggressive, zero-cost stack optimized for a **48–72 hour** hackathon build.

| Layer | Technology |
| --- | --- |
| Channel | Telegram Bot API (or Web Chat UI fallback) |
| Backend | Python 3.13 + FastAPI (Celery optional only) |
| AI / Vision | Google Gemini 2.0 Flash (primary) + Groq Llama Vision (fallback) |
| Speech-to-Text | Groq Whisper-large-v3 (primary) + faster-whisper (local fallback) |
| Text-to-Speech | edge-tts (free Hindi voices) |
| Data | Supabase Postgres (or SQLite) + Upstash Redis (optional) |
| Storage | Supabase Storage or local folder |
| Weather | OpenWeather One Call 3.0 (free tier) |
| Admin | Streamlit (default) — Next.js only as stretch |
| Infra / Deploy | Local + ngrok → Render.com or Railway.app free tier |
| Observability | Basic logging + LangSmith free tier (optional) |

---

## 2. Layer-by-Layer Details

### 2.1 Channel Layer

**Primary: Telegram Bot API**

- Free, instant signup, no Meta business verification required
- Demo-ready in minutes
- Supports text, images, audio

**Fallback:** Browser Web Chat at `/chat` (text, image URL, demo location). Voice notes remain Telegram-only.

**Deferred:** Meta WhatsApp Business Cloud API (requires verification — post-hackathon)

### 2.2 Backend Layer

**Core: Python 3.13 + FastAPI + Uvicorn**

- FastAPI handles all webhooks and orchestration
- Pydantic for request validation
- Pillow for image validation and resizing
- ffmpeg for audio format conversion if needed

**Celery:** Optional only. Use FastAPI `BackgroundTasks` by default. Add Celery only if photo processing is too slow for the demo.

### 2.3 AI / ML Layer

All primary models have usable free tiers for a short hackathon demo.

| Capability | Primary | Fallback |
| --- | --- | --- |
| Crop Photo Diagnosis | Gemini 2.0 Flash (Vision) | Groq Llama Vision |
| Text Chat / Advisory | Gemini 2.0 Flash | Groq Llama Chat |
| Speech-to-Text | Groq Whisper-large-v3 | faster-whisper (local) |
| Text-to-Speech | edge-tts (Hindi) | Text-only reply |

### 2.4 Data Layer

- Supabase Postgres free tier (or plain SQLite for maximum simplicity)
- Upstash Redis free tier (optional — only if rate limiting or simple caching is needed)
- Supabase Storage or local folder for temporary media

**No AWS. No paid database. No separate vector database.**

### 2.5 External APIs

- OpenWeather One Call 3.0 — free tier (1,000 calls/day)
- Mandi prices — hardcoded samples or simple cached values for demo

ISRO Bhuvan is explicitly cut for the hackathon.

### 2.6 Admin Dashboard

**Default:** Streamlit — single Python file, fast to build, shows recent conversations and diagnoses.

**Stretch only:** Next.js single page if extra time remains.

### 2.7 Infrastructure

- **Local development:** Docker (optional) + ngrok for webhook tunnel
- **Demo deployment:** Render.com or Railway.app free tier
- No AWS EC2 / RDS / S3 for the hackathon

---

## 3. What Was Removed (and Why)

| Removed / Deferred | Reason |
| --- | --- |
| OpenRouter + GPT-4o / Claude | Paid credits — replaced by Gemini + Groq free tiers |
| Sarvam Bulbul TTS | Paid — replaced by free edge-tts |
| OpenAI Whisper API | Paid — replaced by Groq Whisper + faster-whisper |
| AWS (EC2, RDS, S3, etc.) | Billing + setup time — replaced by Supabase + Render/Railway |
| Full Celery architecture | Over-engineering for demo — FastAPI BackgroundTasks sufficient |
| RAG / pgvector | Not needed for core demo — hardcoded context is enough |
| ISRO Bhuvan | Classic over-engineering — OpenWeather is enough |
| Meta WhatsApp Cloud API | Business verification wait — Telegram Bot API is instant |
| Next.js full admin | Too slow to build — Streamlit is dramatically faster |

---

## 4. Cost Estimate (Hackathon)

**Total estimated cost for the demo period: $0**

- Telegram Bot API — Free
- Google Gemini free tier — Free
- Groq free tier — Free
- edge-tts — Free (local)
- Supabase free tier — Free
- Render / Railway free tier — Free
- OpenWeather free tier — Free
- ngrok free tier — Free

---

## 5. Post-Hackathon Upgrade Path

- Meta WhatsApp Business Cloud API (real farmer numbers)
- Sarvam Bulbul or Bhashini for higher-quality Hindi TTS
- Paid Gemini / Groq tiers for higher rate limits
- Full Celery + Redis if scale requires it
- Proper RAG with pgvector
- ISRO / satellite data for continuous insights
- Production admin dashboard
