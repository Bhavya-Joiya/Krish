# Proactive Agricultural Nudge Loop — What YOU need to do

This guide is for the **proactive** second loop added on top of the existing reactive Telegram bot.

**Important channel note:** This repo uses **Telegram Bot API** outbound messaging (`send_telegram_text`), not Twilio WhatsApp. The proactive loop reuses that existing messaging layer.

---

## A. What was implemented

A separate proactive loop:

```
APScheduler
  → farmers with lat/lon
  → OPEN advisories?
  → OpenWeather 5-day/3-hour forecast (next 24h)
  → Rain rule?
  → Rain ∧ Open-Advisory
  → Hindi contextual nudge
  → send_telegram_text(...)
  → SQLite nudge_events + messages log
```

Reactive features (photo / voice / text / weather / mandi / webchat) are unchanged.

---

## B. Files created / modified

### Created
| Path | Role |
| --- | --- |
| `app/services/forecast.py` | OpenWeather forecast + rain evaluation |
| `app/services/proactive.py` | Nudge rule + message + send + logging |
| `app/services/scheduler.py` | APScheduler singleton + lifespan hooks |
| `scripts/test_proactive.py` | Manual / dry-run / force-rain runner |
| `scripts/seed_advisory.py` | Seed OPEN advisory for a farmer |
| `scripts/test_proactive_rules.py` | Offline rain-rule unit checks |
| `docs/PROACTIVE_LOOP_YOUR_STEPS.md` | This guide |

### Modified
| Path | Change |
| --- | --- |
| `app/db.py` | `advisories`, `nudge_events`, `proactive_runs` tables |
| `app/config.py` | `PROACTIVE_*` settings |
| `app/services/repository.py` | Advisory / nudge / farmer-location helpers |
| `app/main.py` | Start/stop scheduler; health fields |
| `admin/streamlit_app.py` | Proactive Nudges + Advisories tabs |
| `requirements.txt` | `apscheduler>=3.10.4` |
| `.env.example` | Proactive env vars documented |

---

## C. Architecture now

### Reactive (unchanged)
Farmer → Telegram webhook / Web Chat → orchestrator → AI → reply → SQLite

### Proactive (new)
APScheduler job → `run_proactive_check()` → forecast + advisories → Telegram send → SQLite

Proactive logic lives in `app/services/proactive.py` — **not** in the Telegram webhook.

---

## D. What you personally need to do

1. Install new dependency  
2. Confirm `OPENWEATHER_API_KEY` in `.env`  
3. Add proactive env vars (optional; defaults exist)  
4. Restart uvicorn  
5. Ensure a farmer has location + OPEN advisory  
6. Run dry-run / force-rain test  
7. Optionally send a real Telegram nudge  
8. Check Streamlit admin

---

## E. OpenWeather API key

1. Open https://openweathermap.org/api  
2. Create a free account  
3. Generate an API key (Current Weather + 5-day/3-hour forecast on free tier)

---

## F. Where to put the key

In `c:\Krishi\.env`:

```env
OPENWEATHER_API_KEY=your_key_here
```

---

## G. Activation time

New OpenWeather keys can take **up to ~10–30 minutes** (sometimes up to 2 hours) before forecast calls succeed. If you get `401` / `Invalid API key`, wait and retry.

---

## H. Restart Uvicorn

```bat
cd c:\Krishi
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

If port busy: stop the old window (Ctrl+C) first.

---

## I. Start the app (API + tunnel for Telegram reactive)

```bat
cd c:\Krishi
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

Tunnel (other window):

```bat
npx --yes cloudflared tunnel --url http://127.0.0.1:8000
```

Update `APP_PUBLIC_URL`, restart uvicorn, then:

```powershell
curl.exe -X POST http://127.0.0.1:8000/webhooks/telegram/set-webhook
```

(Proactive sending does **not** need the webhook; only reactive inbound does.)

---

## J. Verify scheduler status

```powershell
curl.exe -s http://127.0.0.1:8000/health
```

Expect:

```json
"proactive_enabled": true,
"openweather_configured": true,
"scheduler_running": true,
"proactive_interval_minutes": 15
```

Also: http://127.0.0.1:8000/demo/checklist

---

## K. Test OpenWeather forecast (indirect)

Dry-run will call forecast for farmers with locations:

```bat
.venv\Scripts\python.exe scripts\test_proactive.py --dry-run
```

Look in JSON `details[].forecast_reason` / `forecast_error`.

Offline rain-rule tests (no network):

```bat
.venv\Scripts\python.exe scripts\test_proactive_rules.py
```

---

## L. Create / seed an OPEN advisory

List farmers that already have lat/lon:

```bat
.venv\Scripts\python.exe scripts\seed_advisory.py --list-farmers
```

Seed (replace with your Telegram farmer id from DB / admin):

```bat
.venv\Scripts\python.exe scripts\seed_advisory.py --farmer-id telegram:YOUR_CHAT_ID --crop टमाटर --title "टमाटर सिंचाई सलाह"
```

List advisories:

```bat
.venv\Scripts\python.exe scripts\seed_advisory.py --list
```

---

## M. Ensure farmer has latitude / longitude

On Telegram, open your bot and **share location** (📎 → Location).

Or confirm in admin / SQLite `farmers` table.

Farmer id format: `telegram:<chat_id>`

---

## N. Run the proactive test script

```bat
cd c:\Krishi
.venv\Scripts\python.exe scripts\test_proactive.py
```

Only one farmer:

```bat
.venv\Scripts\python.exe scripts\test_proactive.py --farmer-id telegram:YOUR_CHAT_ID
```

---

## O. Dry-run (no Telegram send)

```bat
.venv\Scripts\python.exe scripts\test_proactive.py --dry-run
```

```bat
.venv\Scripts\python.exe scripts\test_proactive.py --farmer-id telegram:YOUR_CHAT_ID --dry-run --force-rain
```

Dry-run still evaluates forecast + open advisories and prints the message that **would** be sent. It logs `delivery_status=dry_run` (does **not** start cooldown — only `sent` does).

---

## P. Demo mode

In `.env`:

```env
PROACTIVE_DEMO_MODE=true
```

Restart uvicorn. Then rain is treated as true for nudging, while logs still show the **real** OpenWeather rain result.

Or without changing `.env`:

```bat
.venv\Scripts\python.exe scripts\test_proactive.py --force-rain
```

Message is prefixed with `[DEMO MODE]`.

Set back to false for normal judging of real weather:

```env
PROACTIVE_DEMO_MODE=false
```

---

## Q. Real Telegram nudge

Prerequisites:
- Farmer messaged the bot at least once (so chat id exists)
- Location saved
- OPEN advisory seeded
- Rain true **or** `--force-rain` / demo mode
- `TELEGRAM_BOT_TOKEN` configured

```bat
.venv\Scripts\python.exe scripts\test_proactive.py --farmer-id telegram:YOUR_CHAT_ID --force-rain
```

You should receive an unprompted Hindi message in Telegram.

---

## R. Inspect logs

In the uvicorn terminal look for:

```text
[PROACTIVE] Scheduler started
[PROACTIVE] Checking farmers
[PROACTIVE] Farmer ...: open advisory found
[PROACTIVE] Farmer ...: rain detected in next 24h
[PROACTIVE] Farmer ...: sending nudge
[PROACTIVE] Farmer ...: nudge sent
```

---

## S. Inspect SQLite

Default DB: `c:\Krishi\data\smart_crop_bot.db`

```bat
.venv\Scripts\python.exe -c "import sqlite3; c=sqlite3.connect(r'c:\Krishi\data\smart_crop_bot.db'); print(c.execute('SELECT id,farmer_id,title,status FROM advisories').fetchall()); print(c.execute('SELECT id,farmer_id,delivery_status,triggered_at FROM nudge_events ORDER BY id DESC LIMIT 5').fetchall())"
```

---

## T. Verify in Streamlit

```bat
cd c:\Krishi
.venv\Scripts\streamlit.exe run admin\streamlit_app.py
```

Open **Proactive Nudges** and **Advisories** tabs.

---

## U. Troubleshoot OpenWeather

| Symptom | Fix |
| --- | --- |
| `openweather_configured: false` | Set `OPENWEATHER_API_KEY` in `.env`, restart |
| `401` / invalid key | Wait for key activation; regenerate key |
| `forecast_error` in dry-run | Check network; verify key on forecast endpoint |
| No rain ever | Use `--force-rain` or `PROACTIVE_DEMO_MODE=true` for demo |

---

## V. Troubleshoot messaging (Telegram)

| Symptom | Fix |
| --- | --- |
| `telegram_configured: false` | Fix `TELEGRAM_BOT_TOKEN` |
| Send failed / chat not found | Farmer must `/start` the bot first |
| No message | Confirm `--force-rain` or real rain + OPEN advisory |

---

## W. Troubleshoot scheduler

| Symptom | Fix |
| --- | --- |
| `scheduler_running: false` | Ensure `PROACTIVE_ENABLED=true` and app lifespan started |
| Duplicate jobs under reload | Job id uses `replace_existing=True`; restart cleanly |
| Waiting forever | Don’t wait 15 min — use `scripts/test_proactive.py` |

---

## X. Prevent duplicate messages

Cooldown: `PROACTIVE_NUDGE_COOLDOWN_HOURS` (default 24).

After a successful `sent` nudge for that farmer + nudge type, further runs skip with:

`cooldown active, skipping`

Failed / dry-run do **not** block a later real send.

---

## Y. Prepare for judging

1. Pre-seed location (share location in Telegram)  
2. Seed OPEN advisory for that farmer  
3. Keep `PROACTIVE_DEMO_MODE=true` **or** use `--force-rain` if sky is clear  
4. Show dry-run JSON first, then real send  
5. Show Streamlit Proactive Nudges tab  
6. Re-run to show cooldown skip  
7. Mention rule verbally: **Rain-in-24h AND Open-Advisory**

---

## Rain rule (exact)

For each OpenWeather 3-hour forecast point with `now <= dt <= now + PROACTIVE_LOOKAHEAD_HOURS`:

Rain expected if **any** point has:

- `pop >= PROACTIVE_RAIN_POP_THRESHOLD` (default 0.40), **OR**
- rain volume `>= PROACTIVE_RAIN_MM_THRESHOLD` (default 1.0 mm / 3h), **OR**
- weather main/description indicates Rain / Drizzle / Thunderstorm / बारिश

Language uses “बारिश की **संभावना** है” — not certainty.

---

## Boolean acceptance matrix

| Rain | Open advisory | Nudge? |
| --- | --- | --- |
| FALSE | FALSE | NO |
| FALSE | TRUE | NO |
| TRUE | FALSE | NO |
| TRUE | TRUE | YES (if no cooldown) |

---

## Suggested `.env` block

```env
PROACTIVE_ENABLED=true
PROACTIVE_CHECK_INTERVAL_MINUTES=15
PROACTIVE_LOOKAHEAD_HOURS=24
PROACTIVE_RAIN_POP_THRESHOLD=0.40
PROACTIVE_RAIN_MM_THRESHOLD=1.0
PROACTIVE_NUDGE_COOLDOWN_HOURS=24
PROACTIVE_DEMO_MODE=false
```

---

## Exact Windows command cheat-sheet

```bat
cd c:\Krishi
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts\test_proactive_rules.py
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
curl.exe -s http://127.0.0.1:8000/health
.venv\Scripts\python.exe scripts\seed_advisory.py --list-farmers
.venv\Scripts\python.exe scripts\seed_advisory.py --farmer-id telegram:YOUR_CHAT_ID
.venv\Scripts\python.exe scripts\test_proactive.py --farmer-id telegram:YOUR_CHAT_ID --dry-run --force-rain
.venv\Scripts\python.exe scripts\test_proactive.py --farmer-id telegram:YOUR_CHAT_ID --force-rain
.venv\Scripts\streamlit.exe run admin\streamlit_app.py
```
