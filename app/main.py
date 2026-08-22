"""Smart Crop Bot — FastAPI entrypoint (Phase 5: demo-ready)."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.db import init_db
from app.services.prewarm import prewarm_services
from app.services.scheduler import get_scheduler_status, start_scheduler, stop_scheduler
from app.webhooks.telegram import router as telegram_router
from app.webchat.routes import router as webchat_router

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent


def _configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    _configure_logging()
    settings = get_settings()
    Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    init_db()
    logging.getLogger(__name__).info(
        "Smart Crop Bot starting (env=%s, telegram=%s, gemini=%s, groq=%s, weather=%s, proactive=%s)",
        settings.app_env,
        settings.telegram_configured,
        settings.gemini_configured,
        settings.groq_configured,
        settings.openweather_configured,
        settings.proactive_enabled,
    )
    start_scheduler()
    try:
        yield
    finally:
        stop_scheduler()


app = FastAPI(
    title="Smart Crop Bot",
    description="Telegram agricultural advisor — Phase 5 demo-ready MVP",
    version="0.5.0",
    lifespan=lifespan,
)

app.include_router(telegram_router)
app.include_router(webchat_router)

static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
media_dir = PROJECT_ROOT / "media"
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)
media_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>Smart Crop Bot</title>
      <style>
        body { font-family: system-ui, sans-serif; max-width: 640px; margin: 3rem auto; padding: 0 1rem; }
        a { color: #0b6e4f; }
        code { background: #f0f0f0; padding: 0.15rem 0.35rem; border-radius: 4px; }
      </style>
    </head>
    <body>
      <h1>Smart Crop Bot</h1>
      <p>Phase 5 — demo-ready Telegram crop advisor (photo, voice, weather, mandi).</p>
      <p><small>Web Chat backup: text, image URL, location — not voice.</small></p>
      <ul>
        <li>Health: <a href="/health"><code>/health</code></a></li>
        <li>Pre-warm before demo: <code>POST /demo/prewarm</code></li>
        <li>Telegram webhook: <code>POST /webhooks/telegram</code></li>
        <li>Register webhook: <code>POST /webhooks/telegram/set-webhook</code></li>
        <li>Web Chat backup: <a href="/chat"><code>/chat</code></a></li>
      </ul>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    settings = get_settings()
    sched = get_scheduler_status()
    return {
        "status": "ok",
        "phase": 5,
        "version": app.version,
        "telegram_configured": settings.telegram_configured,
        "gemini_configured": settings.gemini_configured,
        "groq_configured": settings.groq_configured,
        "openweather_configured": settings.openweather_configured,
        "tts_enabled": settings.tts_enabled,
        "public_url_set": bool(settings.public_base_url),
        "env": settings.app_env,
        "proactive_enabled": sched["proactive_enabled"],
        "scheduler_running": sched["scheduler_running"],
        "proactive_interval_minutes": sched["proactive_interval_minutes"],
        "proactive_demo_mode": sched["proactive_demo_mode"],
        "fallbacks": {
            "vision_chat": "gemini→groq",
            "stt": "groq-whisper→faster-whisper(optional)",
            "tts": "edge-tts→text-only",
            "weather": "openweather→polite Hindi error",
        },
    }


@app.post("/demo/prewarm")
async def demo_prewarm():
    """Call once 1–2 minutes before the live demo to wake free-tier models."""
    result = await prewarm_services()
    return {"ok": True, "prewarm": result}


@app.get("/demo/checklist")
async def demo_checklist():
    settings = get_settings()
    sched = get_scheduler_status()
    checks = [
        {"id": "telegram", "ok": settings.telegram_configured, "hint": "TELEGRAM_BOT_TOKEN in .env"},
        {"id": "gemini", "ok": settings.gemini_configured, "hint": "GEMINI_API_KEY"},
        {"id": "groq", "ok": settings.groq_configured, "hint": "GROQ_API_KEY (STT+fallback)"},
        {"id": "public_url", "ok": bool(settings.public_base_url), "hint": "APP_PUBLIC_URL / tunnel / Render URL"},
        {"id": "weather", "ok": settings.openweather_configured, "hint": "OPENWEATHER_API_KEY"},
        {"id": "tts", "ok": settings.tts_enabled, "hint": "TTS_ENABLED=true"},
        {
            "id": "proactive",
            "ok": settings.proactive_enabled and settings.openweather_configured,
            "hint": "PROACTIVE_ENABLED + OPENWEATHER_API_KEY",
        },
        {
            "id": "scheduler",
            "ok": sched["scheduler_running"] or not settings.proactive_enabled,
            "hint": "APScheduler starts with FastAPI lifespan",
        },
    ]
    return {
        "ready": all(c["ok"] for c in checks if c["id"] in {"telegram", "gemini", "public_url"}),
        "checks": checks,
        "demo_order": [
            "1. Crop leaf photo → Hindi diagnosis",
            "2. Hindi voice note → transcript + advice (+ voice)",
            "3. Location + आज मौसम कैसा है?",
            "4. टमाटर का मंडी भाव?",
            "5. Streamlit admin refresh",
            "6. Backup: /chat (text, image URL — no voice)",
            "7. Proactive: seed OPEN advisory + run scripts/test_proactive.py",
        ],
    }
