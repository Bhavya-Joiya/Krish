# Smart Crop Bot

AI-powered WhatsApp agricultural advisor for Indian farmers (hackathon MVP).

Farmers send a **photo**, **Hindi voice note**, or **text** — and get practical advice back inside WhatsApp. No app download.

## Docs

| Doc | Description |
| --- | --- |
| [docs/01_Product_Idea.md](docs/01_Product_Idea.md) | Product idea |
| [docs/02_Tech_Stack.md](docs/02_Tech_Stack.md) | Tech stack |
| [docs/03_Application_Workflow.md](docs/03_Application_Workflow.md) | Workflows |
| [docs/04_PRD.md](docs/04_PRD.md) | PRD |
| [docs/05_Implementation_Plan.md](docs/05_Implementation_Plan.md) | 5-phase plan |
| [docs/PHASE1_YOUR_STEPS.md](docs/PHASE1_YOUR_STEPS.md) | Phase 1 setup |
| [docs/PHASE2_YOUR_STEPS.md](docs/PHASE2_YOUR_STEPS.md) | Phase 2 setup |
| [docs/PHASE3_YOUR_STEPS.md](docs/PHASE3_YOUR_STEPS.md) | Phase 3 setup |
| [docs/PHASE4_YOUR_STEPS.md](docs/PHASE4_YOUR_STEPS.md) | Phase 4 setup |
| [docs/PHASE5_YOUR_STEPS.md](docs/PHASE5_YOUR_STEPS.md) | **Phase 5 deploy + demo** |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | Live demo script |
| [docs/PITCH.md](docs/PITCH.md) | Pitch paragraph |

## Features (MVP)

- Crop photo → Hindi diagnosis (Gemini, Groq fallback)
- Text chat (Hindi/English)
- Voice in (Groq Whisper) + Hindi voice out (edge-tts)
- Weather (OpenWeather) + demo mandi prices
- SQLite logging + Streamlit admin
- Web Chat backup at `/chat` (text, image URL, location — voice is WhatsApp only)
- Deduped webhooks + light rate limit + `/demo/prewarm`

## Quick start

```bat
cd c:\Krishi
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

Fill `.env` (Twilio, Gemini, Groq, OpenWeather, `APP_PUBLIC_URL`).

```bat
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: http://127.0.0.1:8000/health  
- Checklist: http://127.0.0.1:8000/demo/checklist  
- Web Chat: http://127.0.0.1:8000/chat  
- Prewarm: `.venv\Scripts\python.exe scripts\prewarm.py`  
- Admin: `.venv\Scripts\streamlit.exe run admin\streamlit_app.py`  

Twilio webhook: `POST /webhooks/twilio/whatsapp`

## Deploy (Phase 5)

- **Render:** `render.yaml` or manual web service (see `docs/PHASE5_YOUR_STEPS.md`)
- **Railway:** `railway.toml`
- Set `APP_PUBLIC_URL` to the public HTTPS URL and point Twilio at `/webhooks/twilio/whatsapp`

## Demo order

1. Leaf photo → diagnosis  
2. Hindi voice note  
3. Location + weather  
4. Mandi prices  
5. Streamlit admin  
6. Backup `/chat` if sandbox fails (text + image URL; voice WhatsApp-only)
