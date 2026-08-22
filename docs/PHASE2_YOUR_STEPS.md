# Phase 2 — What YOU need to do (step by step)

Phase 2 code is already in the repo: **crop photo diagnosis + text chat** (Gemini primary, Groq fallback).

**Goal:** Send a leaf photo on WhatsApp → Hindi diagnosis in ~8–15 seconds. Ask text questions → useful advice.

---

## Step 0 — Keep Phase 1 running pieces

You still need:

1. Twilio WhatsApp Sandbox joined on your phone  
2. FastAPI on port 8000  
3. ngrok HTTPS tunnel → Twilio webhook  
   `https://YOUR_NGROK_URL/webhooks/twilio/whatsapp`

If those already work from Phase 1, continue.

---

## Step 1 — Get a Gemini API key (required)

### You do

1. Open [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with Google
3. Click **Create API key**
4. Copy the key

### Done when

- You have a key starting something like `AIza…`

---

## Step 2 — Get a Groq API key (strongly recommended fallback)

### You do

1. Open [https://console.groq.com/keys](https://console.groq.com/keys)
2. Create an API key
3. Copy it

If Groq is skipped, Gemini alone still works; fallback only matters if Gemini rate-limits during demo.

---

## Step 3 — Put keys in `.env`

### You do

Open `c:\Krishi\.env` and set:

```env
GEMINI_API_KEY=paste_gemini_key_here
GROQ_API_KEY=paste_groq_key_here
```

Keep your existing Twilio + `APP_PUBLIC_URL` values.

Save the file.

### Done when

- Both keys are filled (or at least `GEMINI_API_KEY`)

---

## Step 4 — Install new Python packages

### You do (cmd)

```bat
cd c:\Krishi
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

Or without activate:

```bat
cd c:\Krishi
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Done when

- Install finishes without errors  
- `pip show google-genai pillow groq` shows packages

---

## Step 5 — Restart the app (required after .env change)

### You do

Stop any old server (Ctrl+C), then:

```bat
cd c:\Krishi
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

Open: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

You want something like:

```json
{
  "status": "ok",
  "phase": 2,
  "twilio_configured": true,
  "gemini_configured": true,
  "groq_configured": true
}
```

### Done when

- `"phase": 2`
- `"gemini_configured": true`

---

## Step 6 — Confirm ngrok + Twilio webhook still point here

### You do

1. In a second terminal, run your working ngrok (full path if needed):
   ```bat
   C:\Tools\ngrok\ngrok.exe http 8000
   ```
   (or whatever path worked for you)
2. If the ngrok URL **changed**, update:
   - `.env` → `APP_PUBLIC_URL=https://….ngrok-free.app`
   - Twilio Sandbox webhook → `https://….ngrok-free.app/webhooks/twilio/whatsapp`
3. Restart uvicorn after changing `.env`

### Done when

- Visiting `https://YOUR_NGROK_URL/health` shows Phase 2 JSON

---

## Step 7 — Live WhatsApp tests (Phase 2 acceptance)

### You do

From the sandbox-joined phone:

| Test | Send | Expect |
| --- | --- | --- |
| A | Text: `टमाटर में पत्ते पीले क्यों हो रहे हैं?` | Short Hindi farming advice |
| B | Clear photo of a diseased leaf | Diagnosis name + क्या करें steps in Hindi |
| C | Random non-crop photo (e.g. selfie) | Polite ask for a clear crop/leaf photo |
| D | Voice note | Placeholder saying voice comes in Phase 3 |

Watch the uvicorn terminal for logs like `Gemini diagnosis ok` or `Groq diagnosis ok`.

### Done when (Phase 2 complete)

- [ ] Text question gets a useful Hindi/English reply  
- [ ] Leaf photo gets diagnosis + actions  
- [ ] Bad photo gets a polite “clear photo” style message  
- [ ] No crash in the server logs  

---

## Step 8 — Backup test without WhatsApp

### You do

1. Open [http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)
2. **Text mode:** ask a crop question  
3. **Image mode:** paste a **public direct image URL** of a leaf (must be openly downloadable)  
4. **Location mode:** demo weather query (voice not supported in Web Chat)

Voice notes work on **WhatsApp only**, not in the browser backup.

---

## Common problems

| Problem | What you do |
| --- | --- |
| `gemini_configured: false` | Key missing/wrong in `.env`; restart uvicorn |
| Photo never answered | Check ngrok still running; check server logs for download/AI errors |
| `429` / rate limit | Wait a minute; ensure `GROQ_API_KEY` is set for fallback |
| Web chat image fails | URL must be public HTTPS ending in a real image, not a Google Drive preview page |
| Reply too slow | Normal up to ~15s on free tier; webhook uses background task so Twilio won’t time out as easily |

---

## What the agent built for Phase 2

| Path | Role |
| --- | --- |
| `app/services/media.py` | Download Twilio / public media |
| `app/services/image_pipeline.py` | Pillow validate + resize |
| `app/services/gemini_client.py` | Primary vision + chat |
| `app/services/groq_client.py` | Fallback vision + chat |
| `app/services/orchestrator.py` | Routes image/text to AI |
| `app/services/reply_format.py` | Formats diagnosis JSON → WhatsApp Hindi |
| `app/webhooks/twilio.py` | Background AI reply send |
| `app/webchat/routes.py` | Same AI via browser |

---

## After Phase 2 works

Say: **“Phase 2 works — start Phase 3”**  
Phase 3 adds voice note understanding (Whisper) and Hindi voice replies (edge-tts).
