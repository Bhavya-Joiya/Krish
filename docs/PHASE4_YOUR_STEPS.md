# Phase 4 — What YOU need to do (step by step)

Phase 4 code is in the repo: **weather**, **mandi demo prices**, **SQLite logging**, **Streamlit admin**.

**Goal:** Ask “आज मौसम कैसा है?” / “टमाटर का भाव?” and see conversations in the admin page.

---

## Step 0 — Keep earlier phases running

You still need:

1. One uvicorn on port **8000** running **latest code** (`"phase": 4` on `/health`)  
2. HTTPS tunnel + Telegram webhook  
3. `GEMINI_API_KEY` + `GROQ_API_KEY`  

If `/health` still shows phase 2/3, stop old uvicorn (Ctrl+C) and restart after Step 2.

---

## Step 1 — Get OpenWeather API key (for live weather)

### You do

1. Sign up: [https://openweathermap.org/api](https://openweathermap.org/api)  
2. Create a free key under **Current Weather Data**  
3. Keys can take **10–60 minutes** to activate after creation  

### Done when

- You have an OpenWeather API key  

---

## Step 2 — Update `.env` and install packages

### You do

In `c:\Krishi\.env` add/set:

```env
OPENWEATHER_API_KEY=your_openweather_key
```

Then:

```bat
cd c:\Krishi
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Done when

- `pip show streamlit` works  
- Key saved in `.env`  

---

## Step 3 — Restart FastAPI (Phase 4)

### You do

Stop every old uvicorn, then:

```bat
cd c:\Krishi
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/health  

Expect:

```json
{
  "status": "ok",
  "phase": 4,
  "openweather_configured": true,
  ...
}
```

### Done when

- `"phase": 4`  
- `"openweather_configured": true` (after key is set)  

---

## Step 4 — Start Streamlit admin (second terminal)

### You do

```bat
cd c:\Krishi
.venv\Scripts\streamlit.exe run admin\streamlit_app.py
```

Browser opens (usually http://localhost:8501).

### Done when

- Admin page loads with Conversations / Diagnoses tabs  

---

## Step 5 — Telegram acceptance tests

| Test | Send | Expect |
| --- | --- | --- |
| A | Location pin (📎 → Location) | “लोकेशन सेव हो गई” |
| B | `आज मौसम कैसा है?` | Hindi weather summary (or ask for location if A skipped) |
| C | `टमाटर का मंडी भाव क्या है?` | Demo mandi prices in Hindi |
| D | Crop photo | Diagnosis still works; appears under Diagnoses in admin |
| E | Any text/voice | Shows under Conversations after Refresh |

### Done when (Phase 4 complete)

- [ ] Weather works with saved location  
- [ ] Mandi sample reply works  
- [ ] Admin shows messages + diagnoses  

---

## Common problems

| Problem | What you do |
| --- | --- |
| Weather says key not set | Add `OPENWEATHER_API_KEY`, restart uvicorn |
| Weather unavailable right after signup | Wait for key activation; retry later |
| Admin empty | Send a Telegram message first; click Refresh; confirm same DB path |
| Still `phase: 2` | Old server on 8000 — Ctrl+C all uvicoorns, start one Phase 4 process |
| Mandi looks “fake” | Expected for MVP — hardcoded demo samples |

---

## What the agent built

| Path | Role |
| --- | --- |
| `app/db.py` | SQLite schema |
| `app/services/repository.py` | farmers / messages / diagnoses |
| `app/services/intent.py` | weather vs mandi vs general |
| `app/services/weather.py` | OpenWeather current conditions |
| `app/services/mandi.py` | Demo mandi prices |
| `admin/streamlit_app.py` | Admin UI |
| `data/smart_crop_bot.db` | Created at runtime |

---

## After Phase 4 works

Say: **“Phase 4 works — start Phase 5”**  
Phase 5 is deploy polish, fallbacks rehearsal, and demo pack.
