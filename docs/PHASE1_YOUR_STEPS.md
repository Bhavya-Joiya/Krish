# Phase 1 — What YOU need to do (step by step)

This guide is only the **manual actions on your machine / accounts**.  
The Phase 1 code is already in the repo.

**Goal of Phase 1:** Send a WhatsApp message → your FastAPI app receives it → bot replies in Hindi. No AI yet.

---

## Step 0 — Prerequisites (do once)

### You do

1. Confirm **Python 3.11+** is installed (`python --version`).
2. Install **Git** if you want version control later (optional for Phase 1).
3. Create a free **Twilio** account: [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
4. Install **ngrok** (needed so Twilio can reach your laptop):
   - Download: [https://ngrok.com/download](https://ngrok.com/download)
   - Or: `winget install ngrok.ngrok`
5. Sign up at [https://dashboard.ngrok.com](https://dashboard.ngrok.com), copy your **authtoken**, then run:
   ```powershell
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

### Done when

- Twilio account exists  
- `ngrok version` works in PowerShell  
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
3. Leave Twilio fields empty for now if you have not opened the Console yet — you will fill them in Step 3.
4. **Never commit** `.env` (already in `.gitignore`).

### Done when

- `.env` exists next to `requirements.txt`  

---

## Step 3 — Twilio WhatsApp Sandbox credentials

### You do

1. Open [Twilio Console](https://console.twilio.com/).
2. Copy **Account SID** and **Auth Token** (dashboard home).
3. Paste into `.env`:
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxx
   TWILIO_AUTH_TOKEN=your_token
   ```
4. Go to **Messaging → Try it out → Send a WhatsApp message**  
   (or search “WhatsApp Sandbox”).
5. Note the sandbox number (often `+1 415 523 8886`).
6. Set in `.env`:
   ```env
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   ```
   (Use **your** sandbox number if different; keep the `whatsapp:` prefix.)
7. On the Sandbox page, find the join code like:  
   `join <two-words>`
8. On **your phone WhatsApp**, send that exact message to the sandbox number.
9. Wait for Twilio’s confirmation that you joined the sandbox.
10. Keep this page open — you will paste the webhook URL in Step 6.

### Done when

- Sandbox shows your phone as a joined participant  
- `.env` has SID, token, and `TWILIO_WHATSAPP_FROM`  

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

- [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → should show `"status":"ok"` and `"twilio_configured":true`
- [http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat) → Web Chat fallback (text, image URL, location — no voice)

**Leave this terminal running.**

### Done when

- `/health` returns OK  
- Web Chat page loads  

---

## Step 5 — Expose localhost with ngrok

### You do

1. Open a **second** PowerShell window (do not stop uvicorn).
2. Run:
   ```powershell
   ngrok http 8000
   ```
3. Copy the **HTTPS** forwarding URL, e.g.  
   `https://abc123.ngrok-free.app`
4. Put it in `.env`:
   ```env
   APP_PUBLIC_URL=https://abc123.ngrok-free.app
   ```
5. Restart uvicorn once after changing `.env` (Ctrl+C, then start again), **or** rely on `--reload` if it picks up env (safer to restart).
6. Visit `https://YOUR_NGROK_URL/health` in the browser — should match local health.

> If ngrok shows a browser interstitial (“Visit Site”), click through once from your PC. Twilio POSTs usually still work; if webhooks fail, use an ngrok paid plan or the “skip browser warning” header docs.

### Done when

- Public `/health` works over HTTPS  

---

## Step 6 — Point Twilio webhook to your app

### You do

1. Twilio Console → WhatsApp Sandbox settings.
2. **When a message comes in** webhook URL:
   ```text
   https://YOUR_NGROK_URL/webhooks/twilio/whatsapp
   ```
3. Method: **HTTP POST**
4. Save.
5. (Optional later) set `TWILIO_VALIDATE_SIGNATURE=true` in `.env` **after** `APP_PUBLIC_URL` is correct and matching the ngrok URL Twilio calls.

### Done when

- Sandbox “comes in” URL ends with `/webhooks/twilio/whatsapp`  

---

## Step 7 — Live WhatsApp test (Phase 1 acceptance)

### You do

From the phone that joined the sandbox, send these one by one and watch the **uvicorn terminal logs**:

| Send | Expect on WhatsApp | Expect in logs |
| --- | --- | --- |
| Text: `नमस्ते` | Hindi ack that message was received | `type=text` |
| A crop leaf **photo** | Hindi ack that photo was received | `type=image` + `media_url=...` |
| A short **voice note** | Hindi ack that voice was received | `type=audio` + `media_url=...` |
| (Optional) **Location** pin | Hindi ack that location was received | `type=location` |

### Done when (Phase 1 complete)

- [ ] Text round-trip works  
- [ ] Image media URL is logged  
- [ ] Audio media URL is logged  
- [ ] Secrets are only in `.env`, not in code  

---

## Step 8 — If WhatsApp Sandbox fails (backup)

### You do

1. Open [http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)
2. Choose **Text**, **Image** (public photo URL), or **Location** → Send  
3. Confirm the bot reply appears in the chat panel  

Voice notes are **not** supported in Web Chat (WhatsApp only). Use text for the backup demo path.

Use this for demos if Twilio participant limits block you.

---

## Common problems (quick fixes)

| Problem | What you do |
| --- | --- |
| `twilio_configured: false` | Fill `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` in `.env`, restart uvicorn |
| No reply on WhatsApp | Confirm you sent `join ...` to sandbox; check webhook URL; check ngrok still running |
| Twilio error 21211 / invalid `From` | Fix `TWILIO_WHATSAPP_FROM=whatsapp:+1...` format |
| 403 signature errors | Set `TWILIO_VALIDATE_SIGNATURE=false` for local demo |
| ngrok URL changed | Update Twilio webhook **and** `APP_PUBLIC_URL`, restart |
| Activate.ps1 blocked | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## What the agent already built for you

| Path | Purpose |
| --- | --- |
| `app/main.py` | FastAPI app, `/health`, home page |
| `app/config.py` | Loads `.env` |
| `app/webhooks/twilio.py` | WhatsApp webhook + Hindi ack |
| `app/services/messaging.py` | Sends WhatsApp replies via Twilio |
| `app/services/message_types.py` | Detects text / image / audio / location |
| `app/webchat/` + `templates/chat.html` | Browser fallback chat |
| `.env.example` | Template for your secrets |
| `requirements.txt` | Python dependencies |

---

## After Phase 1 succeeds

Tell the agent: **“Phase 1 works — start Phase 2”**  
Phase 2 adds Gemini photo diagnosis + text advice (the wow demo).
