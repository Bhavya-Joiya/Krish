"""Smart Crop Bot — FastAPI entrypoint (Phase 5: demo-ready)."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.db import init_db
from app.db_sa import init_sqlalchemy
from app.services.prewarm import prewarm_services
from app.services.scheduler import get_scheduler_status, start_scheduler, stop_scheduler
from app.webhooks.telegram import router as telegram_router
from app.webchat.routes import router as webchat_router

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
logger = logging.getLogger(__name__)

_STUB_LANDING = """
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
        <li>Landing channels API: <a href="/api/channels"><code>/api/channels</code></a></li>
        <li>React landing: run <code>npm run build</code> in <code>frontend/</code>, or <code>npm run dev</code> on port 5173</li>
      </ul>
    </body>
    </html>
    """


def _spa_index() -> Path | None:
    index = FRONTEND_DIST / "index.html"
    return index if index.is_file() else None


def _frontend_public_file(relative: str) -> Path | None:
    """Return a file under frontend/dist, or None if missing / path escape."""
    if not relative or ".." in relative.replace("\\", "/").split("/"):
        return None
    try:
        dest = (FRONTEND_DIST / relative).resolve()
        dest.relative_to(FRONTEND_DIST.resolve())
    except (OSError, ValueError):
        return None
    return dest if dest.is_file() else None


def _cors_origins() -> list[str]:
    origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ]
    public = get_settings().public_base_url
    if public:
        origins.append(public)
    return origins


def _media_directory() -> Path:
    path = Path(get_settings().media_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path

# Cached Telegram @username from getMe (without leading @)
_telegram_username_cache: str | None = None


def _configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _resolve_telegram_username() -> str:
    """Return bot username for t.me links (env override, then getMe cache)."""
    global _telegram_username_cache
    settings = get_settings()
    configured = (settings.telegram_bot_username or "").strip().lstrip("@")
    if configured:
        return configured
    if _telegram_username_cache:
        return _telegram_username_cache
    if not settings.telegram_configured:
        return ""
    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.get(f"{settings.telegram_api_base}/getMe")
            data = response.json()
        if data.get("ok") and isinstance(data.get("result"), dict):
            username = (data["result"].get("username") or "").strip()
            if username:
                _telegram_username_cache = username
                return username
    except Exception:
        logger.exception("Failed to resolve Telegram bot username via getMe")
    return ""


@asynccontextmanager
async def lifespan(_: FastAPI):
    _configure_logging()
    settings = get_settings()
    Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    init_db()
    init_sqlalchemy()
    logging.getLogger(__name__).info(
        "Smart Crop Bot starting (env=%s, telegram=%s, gemini=%s, groq=%s, weather=%s, mandi=%s, proactive=%s)",
        settings.app_env,
        settings.telegram_configured,
        settings.gemini_configured,
        settings.groq_configured,
        settings.openweather_configured,
        settings.data_gov_configured,
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

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_origin_regex=(
        r"https://.*\.(onrender\.com|vercel\.app)"
        if _settings.app_env.lower() == "production"
        else None
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telegram_router)
app.include_router(webchat_router)

static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/media", StaticFiles(directory=str(_media_directory())), name="media")
templates = Jinja2Templates(directory=str(templates_dir))

_frontend_assets = FRONTEND_DIST / "assets"
if _frontend_assets.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_frontend_assets)), name="frontend_assets")


@app.get("/", response_class=HTMLResponse)
async def root():
    index = _spa_index()
    if index is not None:
        return FileResponse(
            index,
            media_type="text/html",
            headers={"Cache-Control": "no-cache"},
        )
    return HTMLResponse(_STUB_LANDING)


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
        "data_gov_configured": settings.data_gov_configured,
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
            "mandi": "agmarknet→24h cache",
        },
    }


@app.get("/api/channels")
async def api_channels():
    """Channel cards for the React landing page (Telegram, Web Chat, SMS)."""
    settings = get_settings()
    username = _resolve_telegram_username()
    telegram_ok = settings.telegram_configured and bool(username)
    telegram_href = f"https://t.me/{username}" if username else None
    handle = f"@{username}" if username else "@your_bot"

    return {
        "ok": True,
        "backend": {
            "telegram_configured": settings.telegram_configured,
            "gemini_configured": settings.gemini_configured,
            "groq_configured": settings.groq_configured,
            "openweather_configured": settings.openweather_configured,
            "data_gov_configured": settings.data_gov_configured,
            "public_url_set": bool(settings.public_base_url),
        },
        "channels": [
            {
                "id": "telegram",
                "name": "Telegram Bot",
                "icon": "telegram",
                "status": "connected" if telegram_ok else "offline",
                "meta1": f"Photo · voice · text · weather · mandi · {handle}",
                "meta2": "Primary channel — open the bot in Telegram",
                "href": telegram_href,
                "actionLabel": "Open Telegram" if telegram_ok else "Bot offline",
                "disabled": not telegram_ok,
                "note": (
                    None
                    if telegram_ok
                    else "Set TELEGRAM_BOT_TOKEN (and optionally TELEGRAM_BOT_USERNAME) in .env, then restart the API."
                ),
            },
            {
                "id": "fallback",
                "name": "Fallback Web Chat",
                "icon": "fallback",
                "status": "connected",
                "meta1": "Text + image URL + location — same AI pipeline",
                "meta2": "Voice notes are Telegram-only",
                "href": "/chat",
                "actionLabel": "Open Web Chat",
                "disabled": False,
                "note": "Use this if Telegram is unreachable. Photo via public image URL; no voice upload.",
            },
            {
                "id": "sms",
                "name": "SMS",
                "icon": "sms",
                "status": "pending",
                "meta1": "Text-only advisory — not wired yet",
                "meta2": "Coming soon",
                "href": None,
                "actionLabel": "Coming soon",
                "disabled": True,
                "note": "SMS channel is planned but not built for this demo.",
            },
        ],
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
        {"id": "mandi", "ok": settings.data_gov_configured, "hint": "DATA_GOV_IN_API_KEY"},
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
            "4. टमाटर का मंडी भाव? (Agmarknet live / 24h cache)",
            "5. Streamlit admin refresh",
            "6. Backup: /chat (text, image URL — no voice)",
            "7. Proactive: seed OPEN advisory + run scripts/test_proactive.py",
        ],
    }


@app.get("/{spa_file:path}")
async def frontend_public_file(spa_file: str):
    """Serve extra Vite public files (favicon, icons, …) from frontend/dist."""
    path = _frontend_public_file(spa_file)
    if path is None:
        raise HTTPException(status_code=404)
    return FileResponse(path)
