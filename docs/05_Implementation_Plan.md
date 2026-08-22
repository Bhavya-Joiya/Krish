# Smart Crop Bot — Implementation Plan (5 Phases)

Build the hackathon MVP in five sequential, doable phases. Each phase ends with a clear deliverable you can demo or verify before moving on.

**Product:** AI WhatsApp agricultural advisor (photo diagnosis, voice, text, weather, mandi, admin)  
**Constraint:** Free-tier stack · ~48–72 hours · Scope Lock from PRD  
**Primary wow demo:** Photo → Hindi diagnosis in 8–15 seconds

---

## Phase overview

| Phase | Focus | Outcome | Suggested effort |
| --- | --- | --- | --- |
| 1 | Foundation & channel | WhatsApp ↔ FastAPI round-trip works | ~8–12 hrs |
| 2 | Core AI brain | Photo diagnosis + text chat work | ~10–14 hrs |
| 3 | Voice (STT + TTS) | Voice in and voice out work | ~8–10 hrs |
| 4 | Tools & persistence | Weather, mandi, DB, admin | ~6–8 hrs |
| 5 | Polish, deploy & demo | Live demo-ready + fallbacks | ~6–8 hrs |

---

## Phase 1 — Foundation & WhatsApp Channel

**Goal:** A farmer message reaches FastAPI and a reply comes back on WhatsApp. No AI yet.

### Build

1. **Repo & project layout**
   - Python 3.13 + FastAPI + Uvicorn
   - `.env` for secrets (Twilio, later Gemini/Groq/OpenWeather)
   - `requirements.txt` / `pyproject.toml`
   - Basic folder structure, e.g.:
     - `app/main.py`
     - `app/webhooks/twilio.py`
     - `app/services/` (empty stubs)
     - `app/config.py`

2. **Twilio WhatsApp Sandbox**
   - Create Twilio account + WhatsApp Sandbox
   - Join sandbox from demo phone(s)
   - Confirm media (image/audio) is allowed

3. **Webhook endpoint**
   - `POST /webhooks/twilio/whatsapp`
   - Parse: `From`, `Body`, `NumMedia`, `MediaUrl0`, `MediaContentType0`
   - Detect type: text / image / audio / location
   - Reply with a hard-coded Hindi ack via Twilio (e.g. “संदेश मिल गया। जल्द जवाब भेजेंगे।”)

4. **Local tunnel**
   - Run FastAPI locally
   - Expose with ngrok
   - Point Twilio webhook URL to ngrok → FastAPI

5. **Optional safety net**
   - Browser Web Chat at `/chat` for text, image URL, and demo location (no voice upload)

### Done when

- [ ] Text from WhatsApp → FastAPI → reply on WhatsApp works
- [ ] Image and audio media URLs are received and logged
- [ ] Config loads from env; no secrets in code

### Exit deliverable

“Hello WhatsApp” demo: send any message, get an instant bot reply.

---

## Phase 2 — Core AI Brain (Photo Diagnosis + Text Chat)

**Goal:** Deliver the product’s main wow: photo → diagnosis, and text Q&A in Hindi/Hinglish.

### Build

1. **Media download & image pipeline**
   - Download image from Twilio media URL (auth if required)
   - Validate/resize with Pillow (reject non-images, cap size)
   - Save temp file or bytes for vision call

2. **Gemini Vision diagnosis service**
   - Prompt: identify disease/pest, short explanation, confidence, 2–4 practical steps
   - Force farmer-friendly **Hindi / Hinglish** output
   - Structured parse (JSON if possible) then format a short WhatsApp message

3. **Text advisory service**
   - Gemini 2.0 Flash for Hindi/English questions
   - Short system prompt with agriculture context (hardcoded string; no RAG)
   - Keep replies short (WhatsApp-friendly)

4. **Router / orchestrator**
   - Image → diagnosis flow
   - Text → chat flow
   - Send formatted reply back through Twilio

5. **Fallback (basic)**
   - If Gemini fails → Groq Llama Vision / Chat
   - If both fail → polite Hindi error message

### Done when

- [ ] Clear leaf photo returns disease name + advice in Hindi within ~15s
- [ ] Text questions about crops get useful short replies
- [ ] Bad/non-crop images get a polite “clear leaf photo” style response

### Exit deliverable

Live photo-diagnosis demo (the judge-facing core).

---

## Phase 3 — Voice In & Voice Out

**Goal:** Farmers can talk; bot can reply with Hindi audio.

### Build

1. **Speech-to-Text**
   - Download audio from Twilio media URL
   - Convert OGG/Opus → WAV if needed (ffmpeg)
   - Transcribe with Groq Whisper-large-v3 (Hindi/English)
   - Fallback: local faster-whisper
   - Feed transcript into Phase 2 text flow

2. **Text-to-Speech**
   - edge-tts with a natural Hindi voice
   - Generate audio file from bot reply text
   - Upload/send as WhatsApp voice note via Twilio
   - If TTS fails → text-only (already works)

3. **Reply policy**
   - If inbound was voice → prefer voice + text reply
   - If inbound was text/photo → text primary; optional voice for diagnosis summary

### Done when

- [ ] Hindi voice note → transcript → relevant reply
- [ ] Bot sends a Hindi voice note that is understandable
- [ ] STT/TTS failures degrade gracefully to text

### Exit deliverable

End-to-end voice conversation on WhatsApp.

---

## Phase 4 — Tools, Persistence & Admin

**Goal:** Weather + mandi + logging + Streamlit admin for a complete MVP story.

### Build

1. **Intent helpers on text flow**
   - Detect weather vs mandi vs general advice (LLM intent or simple keywords)
   - **Weather:** OpenWeather One Call 3.0; use saved location or ask farmer to share location pin
   - **Mandi:** hardcoded/cached sample prices (e.g. wheat, tomato, onion for 1–2 mandis)
   - Reply in simple Hindi

2. **Location handling (nice-to-have but small)**
   - On location message: store lat/long against phone number
   - Reuse for weather questions

3. **Data layer**
   - SQLite (fastest) or Supabase Postgres
   - Tables (minimal):
     - `farmers` (phone, location, created_at)
     - `messages` (phone, direction, type, content_summary, created_at)
     - `diagnoses` (phone, result_summary, raw_json, created_at)

4. **Streamlit admin**
   - One page: recent conversations + recent diagnoses
   - Read-only for demo; refreshable list
   - Optional filter by phone

### Done when

- [ ] “आज मौसम कैसा है?” returns a weather reply (or clear location ask)
- [ ] Mandi price question returns sample prices
- [ ] Admin page shows the demo conversation trail

### Exit deliverable

Full MVP feature set per Scope Lock (minus deploy polish).

---

## Phase 5 — Hardening, Deploy & Demo Pack

**Goal:** Stable live demo under free-tier limits; judges understand value in &lt;60 seconds.

### Build

1. **Fallbacks & resilience**
   - Wire all fallbacks from workflow doc:
     - Gemini ↔ Groq
     - Groq Whisper ↔ faster-whisper
     - TTS ↔ text-only
     - OpenWeather ↔ polite Hindi failure message
   - Global try/except → friendly farmer message + log

2. **Demo reliability**
   - Pre-warm API clients before presentation
   - Prepare 3–5 good crop photos (known diseases) for live demo
   - Script the demo path: photo → voice note → weather → admin screen
   - Keep Web Chat UI ready if Twilio Sandbox participant limit bites

3. **Deploy**
   - Deploy FastAPI to Render or Railway free tier
   - Update Twilio webhook to production URL
   - Confirm media download + outbound messages work from cloud
   - Run Streamlit locally or as a second free service for admin

4. **Polish**
   - Consistent Hindi tone and short message formatting
   - Logging for debugging during Q&A
   - README: how to run, env vars, demo steps
   - One-slide / one-paragraph pitch aligned to “photo → 10–15s Hindi diagnosis”

### Done when

- [ ] Photo → diagnosis and voice → reply work on deployed URL
- [ ] No critical crash on the rehearsed demo path
- [ ] Admin shows demo data
- [ ] Backup channel exists if WhatsApp sandbox fails

### Exit deliverable

Demo-ready Smart Crop Bot + pitch script.

---

## Suggested build order (day-by-day for 48–72h)

| Window | Phases | Focus |
| --- | --- | --- |
| Hours 0–12 | Phase 1 | Channel + webhook solid |
| Hours 12–28 | Phase 2 | Photo diagnosis first, then text |
| Hours 28–40 | Phase 3 | STT then TTS |
| Hours 40–52 | Phase 4 | Weather/mandi + DB + Streamlit |
| Hours 52–72 | Phase 5 | Deploy, fallbacks, rehearse |

If time is short, **cut in this order** (keep Scope Lock):

1. Keep: Photo diagnosis (never cut)
2. Keep: Text chat
3. Keep: Voice STT
4. Keep: Voice TTS
5. Stretch: Weather + mandi
6. Stretch: Streamlit polish
7. Cut first if needed: Web Chat UI, Redis, Celery, fancy admin

---

## Team split (optional)

| Role | Owns |
| --- | --- |
| Backend / WhatsApp | Phase 1 webhook, Twilio send/receive, deploy |
| AI / Vision | Phase 2 Gemini prompts, diagnosis formatting, fallbacks |
| Voice | Phase 3 Whisper + edge-tts + ffmpeg |
| Data / Admin | Phase 4 SQLite/Supabase + Streamlit + weather/mandi |
| Demo lead | Phase 5 script, sample photos, rehearsal, backup plan |

---

## Phase acceptance checklist (final)

| # | Capability | Phase |
| --- | --- | --- |
| 1 | WhatsApp text round-trip | 1 |
| 2 | Crop photo → diagnosis + advice (Hindi) | 2 |
| 3 | Text chat (Hindi/English) | 2 |
| 4 | Voice note → text → reply | 3 |
| 5 | Text → Hindi voice reply | 3 |
| 6 | Simple weather reply | 4 |
| 7 | Simple mandi price reply | 4 |
| 8 | Admin view of conversations | 4 |
| 9 | Deployed + fallbacks + demo script | 5 |

When all nine rows are checked, the hackathon Scope Lock MVP is complete.
