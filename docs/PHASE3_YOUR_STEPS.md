# Phase 3 — What YOU need to do (step by step)

Phase 3 code is in the repo: **voice notes → text (Whisper)** and **Hindi voice replies (edge-tts)**.

**Goal:** Send a Hindi voice note on Telegram → bot replies with text + Hindi audio. Photo diagnoses can also get a voice reply.

---

## Step 0 — Keep Phase 1–2 working

You still need:

1. Telegram bot working  
2. One uvicorn on port 8000  
3. HTTPS URL in `.env` as `APP_PUBLIC_URL`  
4. Telegram webhook → `https://YOUR_TUNNEL_URL/webhooks/telegram`  
5. `GEMINI_API_KEY` + `GROQ_API_KEY` set  

**Voice replies upload MP3 directly to Telegram** — no public media URL required for TTS.

---

## Step 1 — Install new packages

### You do (cmd)

```bat
cd c:\Krishi
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This adds `edge-tts` and `imageio-ffmpeg` (bundled ffmpeg — no separate ffmpeg install needed for the main path).

Optional later (local STT fallback, heavy):  
`pip install faster-whisper`  
Skip for the demo if Groq works.

### Done when

- Install finishes without errors

---

## Step 2 — Confirm `.env` has public URL

### You do

Open `c:\Krishi\.env` and ensure:

```env
APP_PUBLIC_URL=https://YOUR_CURRENT_NGROK_HOST
GROQ_API_KEY=...
GEMINI_API_KEY=...
```

Optional Phase 3 knobs (defaults are fine):

```env
TTS_ENABLED=true
TTS_ON_DIAGNOSIS=true
TTS_VOICE=hi-IN-SwaraNeural
```

If the tunnel gave you a **new** URL, update `APP_PUBLIC_URL` and re-register the Telegram webhook.

### Done when

- `APP_PUBLIC_URL` matches the live ngrok HTTPS host (no trailing slash/space)

---

## Step 3 — Restart uvicorn (only one process)

### You do

1. Stop every old server (Ctrl+C in those terminals).  
2. Start one:

```bat
cd c:\Krishi
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Open http://127.0.0.1:8000/health  

Expect something like:

```json
{
  "status": "ok",
  "phase": 3,
  "telegram_configured": true,
  "gemini_configured": true,
  "groq_configured": true,
  "tts_enabled": true,
  "public_url_set": true
}
```

### Done when

- `"phase": 3` and `"public_url_set": true`

---

## Step 4 — Keep ngrok running

### You do

Second terminal:

```bat
C:\Tools\ngrok\ngrok.exe http 8000
```

(or your working ngrok command)

Quick check in browser:

`https://YOUR_NGROK_URL/health` → Phase 3 JSON

---

## Step 5 — Live Telegram tests (Phase 3 acceptance)

| Test | Send | Expect |
| --- | --- | --- |
| A | Hindi **voice note**: “टमाटर में पत्ते पीले हो रहे हैं” | Text with “आपने कहा: …” + advice; then a **voice** reply |
| B | Clear **crop photo** | Text diagnosis + optional Hindi voice note |
| C | Normal **text** question | Text only (no voice) — expected |
| D | Empty / noisy voice | Polite “speak again” Hindi message |

Watch uvicorn logs for: `Groq Whisper ok`, `TTS saved`, `Sent Telegram audio`.

### Done when (Phase 3 complete)

- [ ] Voice note → transcript + useful reply  
- [ ] Voice note also gets audio reply (if `APP_PUBLIC_URL` correct)  
- [ ] Photo still works  
- [ ] Text still works  

---

## Common problems

| Problem | What you do |
| --- | --- |
| Text reply but no voice | Fix `APP_PUBLIC_URL` + restart; confirm `/media/` is reachable via ngrok |
| STT fails | Confirm `GROQ_API_KEY`; try speaking clearer / shorter |
| `phase: 1` or `2` on /health | Old uvicorn still running — kill extras, start one Phase 3 process |
| ngrok interstitial blocks media | Open the ngrok URL once in a browser; free tier can be flaky for media fetch |
| Multiple bots / double replies | Extra uvicorn instances — keep only one |

---

## What the agent built

| Path | Role |
| --- | --- |
| `app/services/stt.py` | Groq Whisper (+ optional local fallback) |
| `app/services/tts.py` | edge-tts Hindi MP3 |
| `app/services/audio_convert.py` | Bundled ffmpeg convert |
| `app/services/orchestrator.py` | Audio → transcript → chat; TTS flags |
| `app/services/messaging.py` | `send_telegram_audio` |
| `media/` + `/media` mount | TTS file storage |

---

## After Phase 3 works

Say: **“Phase 3 works — start Phase 4”**  
Phase 4 adds weather, mandi prices, DB logging, and Streamlit admin.
