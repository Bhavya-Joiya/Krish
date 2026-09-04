"""Project-root entrypoint so `uvicorn main:app` works."""

from app.main import app

__all__ = ["app"]
