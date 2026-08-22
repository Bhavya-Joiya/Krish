# Phase 1 — What YOU need to do (step by step)

This guide is only the **manual actions on your machine / accounts**.  
The Phase 1 code is already in the repo.

**Goal of Phase 1:** Send a Telegram message → your FastAPI app receives it → bot replies in Hindi. No AI yet.

---

## Step 0 — Prerequisites (do once)

### You do

1. Confirm **Python 3.11+** is installed (`python --version`).
2. Install **Git** if you want version control later (optional for Phase 1).
3. Install **Telegram** on your phone (or desktop).
4. Install a public HTTPS tunnel (needed so Telegram can reach your laptop):
   - **Cloudflare (recommended on Windows):** `npx --yes cloudflared tunnel --url http://127.0.0.1:8000`
   - Or double-click `START_DEMO.bat` (starts API + tunnel)
   - Or **ngrok:** [https://ngrok.com/download](https://ngrok.com/download)

### Done when

- Telegram app works on your phone  
- Tunnel command runs without errors  
- Python works  

---

## Step 1 — Create virtualenv & install packages

### You do (in PowerShell)

```powershell
cd c:\Krishi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks the activate script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### Done when

- Prompt shows `(.venv)`  
- `pip show fastapi` prints package info  

---

## Step 2 — Create your `.env` file

### You do

1. Copy the example file:
   ```powershell
   copy .env.example .env
   ```
2. Open `c:\Krishi\.env` in Cursor/Notepad.
3. Leave `TELEGRAM_BOT_TOKEN` empty for now if you have not created the bot yet — you will fill it in Step 3.
4. **Never commit** `.env` (already in `.gitignore`).

### Done when

- `.env` exists next to `requirements.txt`  

---

## Step 3 — Telegram Bot token

### You do

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts (name + username ending in `bot`).
3. Copy the **HTTP API token** BotFather gives you.
4. Paste into `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdef...
   ```
5. Open a chat with your new bot and tap **Start** (or send `/start`).

### Done when

- `.env` has `TELEGRAM_BOT_TOKEN`  
- You can open a chat with your bot in Telegram  

---

## Step 4 — Start the FastAPI server

### You do

In a terminal with venv activated:

```powershell
cd c:\Krishi
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open in browser:

- [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → should show `"status":"ok"` and `"telegram_configured":true`
- [http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat) → Web Chat fallback (text, image URL, location — no voice)

**Leave this terminal running.**

### Done when

- `/health` returns OK  
- Web Chat page loads  

---

## Step 5 — Expose localhost with a tunnel

### You do

1. Open a **second** PowerShell window (do not stop uvicorn).
2. Run:
   ```powershell
   npx --yes cloudflared tunnel --url http://127.0.0.1:8000
   ```
   Or use ngrok: `ngrok http 8000`
3. Copy the **HTTPS** URL, e.g.  
   `https://abc123.trycloudflare.com`
4. Put it in `.env`:
   ```env
   APP_PUBLIC_URL=https://abc123.trycloudflare.com
   ```
5. Restart uvicorn once after changing `.env` (Ctrl+C, then start again).

6. Visit `https://YOUR_TUNNEL_URL/health` in the browser — should match local health.

### Done when

- Public `/health` works over HTTPS  

---

## Step 6 — Register Telegram webhook

### You do

1. With uvicorn running and `APP_PUBLIC_URL` set, register the webhook:
   ```powershell
   curl -X POST https://YOUR_TUNNEL_URL/webhooks/telegram/set-webhook
   ```
   Or open in browser (use a REST client for POST) — the endpoint is `POST /webhooks/telegram/set-webhook`.
2. Confirm response shows `"ok": true` and your webhook URL.

Alternative: call Telegram directly:
```text
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://YOUR_TUNNEL_URL/webhooks/telegram
```

### Done when

- Webhook URL ends with `/webhooks/telegram`  
- [http://127.0.0.1:8000/webhooks/telegram/debug](http://127.0.0.1:8000/webhooks/telegram/debug) shows expected URL  

---

## Step 7 — Live Telegram test (Phase 1 acceptance)

### You do

From Telegram, message your bot and watch the **uvicorn terminal logs**:

| Send | Expect on Telegram | Expect in logs |
| --- | --- | --- |
| Text: `नमस्ते` | Hindi ack / reply | `type=text` |
| A crop leaf **photo** | Hindi ack then diagnosis (Phase 2+) | `type=image` |
| A short **voice note** | Hindi ack then reply (Phase 3+) | `type=audio` |
| **Location** pin | Location saved ack (Phase 4+) | `type=location` |

### Done when (Phase 1 complete)

- [ ] Text round-trip works  
- [ ] Image is received and logged  
- [ ] Audio is received and logged  
- [ ] Secrets are only in `.env`, not in code  

---

## Step 8 — If Telegram fails (backup)

### You do

1. Open [http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)
2. Choose **Text**, **Image** (public photo URL), or **Location** → Send  
3. Confirm the bot reply appears in the chat panel  

Voice notes are **not** supported in Web Chat (Telegram only). Use text for the backup demo path.

---

## Common problems (quick fixes)

| Problem | What you do |
| --- | --- |
| `telegram_configured: false` | Fill `TELEGRAM_BOT_TOKEN` in `.env`, restart uvicorn |
| No reply on Telegram | Check webhook via `/webhooks/telegram/debug`; re-run `set-webhook`; check tunnel still running |
| Tunnel URL changed | Update `APP_PUBLIC_URL`, restart uvicorn, re-register webhook |
| 403 webhook secret | Clear `TELEGRAM_WEBHOOK_SECRET` or match the secret in setWebhook |
| Activate.ps1 blocked | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## What the agent already built for you

| Path | Purpose |
| --- | --- |
| `app/main.py` | FastAPI app, `/health`, home page |
| `app/config.py` | Loads `.env` |
| `app/webhooks/telegram.py` | Telegram webhook + Hindi replies |
| `app/services/messaging.py` | Sends Telegram replies via Bot API |
| `app/services/message_types.py` | Detects text / image / audio / location |
| `app/webchat/` + `templates/chat.html` | Browser fallback chat |
| `.env.example` | Template for your secrets |
| `requirements.txt` | Python dependencies |

---

## After Phase 1 succeeds

Tell the agent: **“Phase 1 works — start Phase 2”**  
Phase 2 adds Gemini photo diagnosis + text advice (the wow demo).
