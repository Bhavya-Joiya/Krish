"""Application settings loaded from environment / .env."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (c:\Krishi)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot API
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    # Optional @username without @ — used for t.me deep links (auto-fetched via getMe if empty)
    telegram_bot_username: str = ""

    # App
    app_env: str = "development"
    app_public_url: str = ""
    log_level: str = "INFO"

    # Phase 2 AI
    gemini_api_key: str = ""
    groq_api_key: str = ""
    # gemini-2.0-flash shut down 2026-06-01; llama-3.3-70b-versatile shut down 2026-08-16
    gemini_model: str = "gemini-3.6-flash"
    groq_chat_model: str = "openai/gpt-oss-120b"
    groq_vision_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    chat_max_output_tokens: int = 4096
    diagnosis_max_output_tokens: int = 2048

    # Phase 3 voice
    groq_whisper_model: str = "whisper-large-v3"
    tts_voice: str = "hi-IN-SwaraNeural"
    tts_enabled: bool = True
    # Also send voice for photo diagnoses (in addition to voice-note replies)
    tts_on_diagnosis: bool = True

    # Phase 4
    openweather_api_key: str = ""
    database_path: str = str(PROJECT_ROOT / "data" / "smart_crop_bot.db")

    # Proactive Agricultural Nudge Loop
    proactive_enabled: bool = True
    proactive_check_interval_minutes: int = 15
    proactive_lookahead_hours: int = 24
    proactive_rain_pop_threshold: float = 0.40
    proactive_rain_mm_threshold: float = 1.0
    proactive_nudge_cooldown_hours: int = 24
    proactive_demo_mode: bool = False

    # Image / media limits
    max_image_bytes: int = 8_000_000
    max_image_dimension: int = 1280
    max_audio_bytes: int = 12_000_000
    media_dir: str = str(PROJECT_ROOT / "media")

    @property
    def telegram_configured(self) -> bool:
        token = (self.telegram_bot_token or "").strip()
        if not token or token in {"your_telegram_bot_token", "changeme"}:
            return False
        return ":" in token and len(token) > 20

    @property
    def gemini_configured(self) -> bool:
        key = (self.gemini_api_key or "").strip()
        return bool(key) and key not in {"your_gemini_api_key", "changeme"}

    @property
    def groq_configured(self) -> bool:
        key = (self.groq_api_key or "").strip()
        return bool(key) and key not in {"your_groq_api_key", "changeme"}

    @property
    def openweather_configured(self) -> bool:
        key = (self.openweather_api_key or "").strip()
        return bool(key) and key not in {"your_openweather_api_key", "changeme"}

    @property
    def public_base_url(self) -> str:
        return (self.app_public_url or "").rstrip("/")

    @property
    def telegram_api_base(self) -> str:
        return f"https://api.telegram.org/bot{(self.telegram_bot_token or '').strip()}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
