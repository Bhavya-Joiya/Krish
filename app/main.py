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
from app.webhooks.twilio import router as twilio_router
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
        "Smart Crop Bot starting (env=%s, twilio=%s, gemini=%s, groq=%s, weather=%s)",
        settings.app_env,
        settings.twilio_configured,
        settings.gemini_configured,
        settings.groq_configured,
        settings.openweather_configured,
    )
    yield


app = FastAPI(
    title="Smart Crop Bot",
    description="WhatsApp agricultural advisor — Phase 5 demo-ready MVP",
    version="0.5.0",
    lifespan=lifespan,
)

app.include_router(twilio_router)
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
      <p>Phase 5 — demo-ready WhatsApp crop advisor (photo, voice, weather, mandi).</p>
      <p><small>Web Chat backup: text, image URL, location — not voice.</small></p>
      <ul>
        <li>Health: <a href="/health"><code>/health</code></a></li>
        <li>Pre-warm before demo: <code>POST /demo/prewarm</code></li>
        <li>Twilio webhook: <code>POST /webhooks/twilio/whatsapp</code></li>
        <li>Web Chat backup: <a href="/chat"><code>/chat</code></a></li>
      </ul>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "ok",
        "phase": 5,
        "version": app.version,
        "twilio_configured": settings.twilio_configured,
        "gemini_configured": settings.gemini_configured,
        "groq_configured": settings.groq_configured,
        "openweather_configured": settings.openweather_configured,
        "tts_enabled": settings.tts_enabled,
        "public_url_set": bool(settings.public_base_url),
        "env": settings.app_env,
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
    checks = [
        {"id": "twilio", "ok": settings.twilio_configured, "hint": "TWILIO_* in .env"},
        {"id": "gemini", "ok": settings.gemini_configured, "hint": "GEMINI_API_KEY"},
        {"id": "groq", "ok": settings.groq_configured, "hint": "GROQ_API_KEY (STT+fallback)"},
        {"id": "public_url", "ok": bool(settings.public_base_url), "hint": "APP_PUBLIC_URL / ngrok / Render URL"},
        {"id": "weather", "ok": settings.openweather_configured, "hint": "OPENWEATHER_API_KEY"},
        {"id": "tts", "ok": settings.tts_enabled, "hint": "TTS_ENABLED=true"},
    ]
    return {
        "ready": all(c["ok"] for c in checks if c["id"] in {"twilio", "gemini", "public_url"}),
        "checks": checks,
        "demo_order": [
            "1. Crop leaf photo → Hindi diagnosis",
            "2. Hindi voice note → transcript + advice (+ voice)",
            "3. Location + आज मौसम कैसा है?",
            "4. टमाटर का मंडी भाव?",
            "5. Streamlit admin refresh",
            "6. Backup: /chat (text, image URL — no voice)",
        ],
    }
