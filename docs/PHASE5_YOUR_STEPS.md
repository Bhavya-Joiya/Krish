# Phase 5 — What YOU need to do (step by step)

Phase 5 code is ready: **hardening**, **prewarm**, **deploy configs**, **demo script + pitch**.

**Goal:** Rehearse a crash-free demo; optionally deploy so you are not dependent on your laptop + ngrok.

---

## Step 1 — Restart on latest Phase 5 code

### You do

Stop old uvicorn, then:

```bat
cd c:\Krishi
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/health → `"phase": 5`

Open http://127.0.0.1:8000/demo/checklist → see readiness flags

### Done when

- `"phase": 5` and core checks are true  

---

## Step 2 — Pre-warm before any live demo

### You do

With the server running:

```bat
cd c:\Krishi
.venv\Scripts\python.exe scripts\prewarm.py --base http://127.0.0.1:8000
```

Or after deploy, point `--base` at your public HTTPS URL.

### Done when

- Prefwarm JSON shows gemini/groq mostly `ok`  

---

## Step 3 — Rehearse the script once

### You do

Follow [DEMO_SCRIPT.md](DEMO_SCRIPT.md) end-to-end:

1. Photo diagnosis  
2. Voice note  
3. Location + weather  
4. Mandi  
5. Streamlit admin  
6. Practice `/chat` backup (text + image URL; voice is Telegram-only)

Put photos in `demo/` (see `demo/README.md`).

### Done when

- Full path works without a critical crash  
- You know your backup line if Telegram fails  

---

## Step 4 — Optional: Deploy to Render (recommended for judging day)

### You do

1. Push this repo to GitHub (or upload).  
2. Create a Web Service on [https://render.com](https://render.com)  
   - Runtime: Python  
   - Build: `pip install -r requirements.txt`  
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`  
   - Or use `render.yaml`  
3. In Render **Environment**, set the same secrets as `.env`:  
   - `TELEGRAM_BOT_TOKEN`
   - `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENWEATHER_API_KEY`  
   - `APP_PUBLIC_URL=https://YOUR-SERVICE.onrender.com`  
   - `DATABASE_PATH=/tmp/smart_crop_bot.db`  
   - `MEDIA_DIR=/tmp/scb_media`  
4. After deploy, register the Telegram webhook:  
   `POST https://YOUR-SERVICE.onrender.com/webhooks/telegram/set-webhook`  
5. Hit `/health` and `scripts\prewarm.py --base https://YOUR-SERVICE.onrender.com`  
6. Test photo + voice on Telegram against the cloud URL  

**Note:** Free Render disks are ephemeral — fine for a demo; data resets on sleep/redeploy. Keep Streamlit admin local if needed:

```bat
.venv\Scripts\streamlit.exe run admin\streamlit_app.py
```

(Local admin only sees local SQLite unless you point `DATABASE_PATH` at shared storage.)

### Railway alternative

Use `railway.toml` + same env vars; start command already set.

### Done when

- Cloud `/health` is phase 5  
- WhatsApp photo works against the deployed webhook  

---

## Step 5 — Pitch readiness

### You do

- Memorize [PITCH.md](PITCH.md) opening paragraph  
- Keep [DEMO_SCRIPT.md](DEMO_SCRIPT.md) open on a second screen  
- Confirm Web Chat backup URL bookmarked  

---

## Acceptance (Phase 5 / full MVP)

- [ ] Photo → diagnosis on stable URL (ngrok or Render)  
- [ ] Voice → reply works  
- [ ] Fallbacks don’t crash the demo (text-only if TTS fails)  
- [ ] Admin shows activity  
- [ ] Backup `/chat` path rehearsed  
- [ ] Prewarm run before presentation  

When these are checked, the hackathon Scope Lock MVP is complete.
