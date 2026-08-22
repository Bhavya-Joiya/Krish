"""SQLite bootstrap for Smart Crop Bot (Phase 4)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import get_settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS farmers (
    phone TEXT PRIMARY KEY,
    latitude REAL,
    longitude REAL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL,
    direction TEXT NOT NULL,
    message_type TEXT NOT NULL,
    content_summary TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS diagnoses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL,
    result_summary TEXT NOT NULL,
    raw_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone);
CREATE INDEX IF NOT EXISTS idx_diagnoses_created ON diagnoses(created_at DESC);

CREATE TABLE IF NOT EXISTS advisories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    crop TEXT,
    advisory_type TEXT NOT NULL DEFAULT 'general',
    status TEXT NOT NULL DEFAULT 'OPEN',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT
);

CREATE TABLE IF NOT EXISTS nudge_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id TEXT NOT NULL,
    advisory_id INTEGER,
    nudge_type TEXT NOT NULL DEFAULT 'rain_open_advisory',
    triggered_at TEXT NOT NULL DEFAULT (datetime('now')),
    rain_detected INTEGER NOT NULL DEFAULT 0,
    forecast_window_hours INTEGER NOT NULL DEFAULT 24,
    delivery_status TEXT NOT NULL,
    message_text TEXT,
    message_id TEXT,
    error TEXT,
    demo_mode INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (advisory_id) REFERENCES advisories(id)
);

CREATE TABLE IF NOT EXISTS proactive_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT,
    farmers_checked INTEGER NOT NULL DEFAULT 0,
    rain_detected_count INTEGER NOT NULL DEFAULT 0,
    nudges_sent INTEGER NOT NULL DEFAULT 0,
    failures INTEGER NOT NULL DEFAULT 0,
    demo_mode INTEGER NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_advisories_farmer_status ON advisories(farmer_id, status);
CREATE INDEX IF NOT EXISTS idx_nudge_events_farmer ON nudge_events(farmer_id, triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_nudge_events_cooldown
    ON nudge_events(farmer_id, advisory_id, nudge_type, triggered_at DESC);
"""


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    path = Path(settings.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()
