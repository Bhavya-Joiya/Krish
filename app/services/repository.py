"""Persistence helpers for farmers, messages, and diagnoses."""

from __future__ import annotations

import logging
from typing import Any

from app.db import get_connection, init_db

logger = logging.getLogger(__name__)

_initialized = False


def ensure_db() -> None:
    global _initialized
    if not _initialized:
        init_db()
        _initialized = True


def upsert_farmer_location(phone: str, latitude: float, longitude: float) -> None:
    ensure_db()
    phone = phone.strip()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO farmers (phone, latitude, longitude, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(phone) DO UPDATE SET
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                updated_at=datetime('now')
            """,
            (phone, latitude, longitude),
        )
        conn.commit()
        logger.info("Saved location for %s lat=%s lon=%s", phone, latitude, longitude)
    finally:
        conn.close()


def get_farmer_location(phone: str) -> tuple[float, float] | None:
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT latitude, longitude FROM farmers WHERE phone = ?",
            (phone.strip(),),
        ).fetchone()
        if not row or row["latitude"] is None or row["longitude"] is None:
            return None
        return float(row["latitude"]), float(row["longitude"])
    finally:
        conn.close()


def log_message(
    phone: str,
    *,
    direction: str,
    message_type: str,
    content_summary: str,
) -> None:
    ensure_db()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO messages (phone, direction, message_type, content_summary)
            VALUES (?, ?, ?, ?)
            """,
            (phone.strip(), direction, message_type, (content_summary or "")[:1000]),
        )
        conn.commit()
    finally:
        conn.close()


def log_diagnosis(phone: str, result_summary: str, raw_json: str | None = None) -> None:
    ensure_db()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO diagnoses (phone, result_summary, raw_json)
            VALUES (?, ?, ?)
            """,
            (phone.strip(), (result_summary or "")[:2000], raw_json),
        )
        conn.commit()
    finally:
        conn.close()


def recent_messages(limit: int = 50, phone: str | None = None) -> list[dict[str, Any]]:
    ensure_db()
    conn = get_connection()
    try:
        if phone:
            rows = conn.execute(
                """
                SELECT id, phone, direction, message_type, content_summary, created_at
                FROM messages
                WHERE phone = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (phone.strip(), limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, phone, direction, message_type, content_summary, created_at
                FROM messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def recent_diagnoses(limit: int = 50, phone: str | None = None) -> list[dict[str, Any]]:
    ensure_db()
    conn = get_connection()
    try:
        if phone:
            rows = conn.execute(
                """
                SELECT id, phone, result_summary, created_at
                FROM diagnoses
                WHERE phone = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (phone.strip(), limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, phone, result_summary, created_at
                FROM diagnoses
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_farmer_phones() -> list[str]:
    ensure_db()
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT DISTINCT phone FROM (
                SELECT phone FROM messages
                UNION
                SELECT phone FROM farmers
                UNION
                SELECT phone FROM diagnoses
            )
            ORDER BY phone
            """
        ).fetchall()
        return [r["phone"] for r in rows]
    finally:
        conn.close()
