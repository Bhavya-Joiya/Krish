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


def list_farmers_with_locations() -> list[dict[str, Any]]:
    """Return farmers that have valid lat/lon (phone is the farmer id)."""
    ensure_db()
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT phone AS farmer_id, latitude, longitude, updated_at
            FROM farmers
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ORDER BY phone
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_advisory(
    farmer_id: str,
    *,
    title: str,
    message: str,
    crop: str | None = None,
    advisory_type: str = "general",
    status: str = "OPEN",
    expires_at: str | None = None,
) -> int:
    ensure_db()
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO advisories (
                farmer_id, title, message, crop, advisory_type, status, expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                farmer_id.strip(),
                title.strip(),
                message.strip(),
                (crop or None),
                advisory_type.strip() or "general",
                status.strip().upper() or "OPEN",
                expires_at,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def get_open_advisories(farmer_id: str) -> list[dict[str, Any]]:
    """OPEN advisories that are not expired (expires_at null or in the future)."""
    ensure_db()
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, farmer_id, title, message, crop, advisory_type, status,
                   created_at, updated_at, expires_at
            FROM advisories
            WHERE farmer_id = ?
              AND UPPER(status) = 'OPEN'
              AND (expires_at IS NULL OR expires_at > datetime('now'))
            ORDER BY id DESC
            """,
            (farmer_id.strip(),),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_advisories(
    *,
    farmer_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    ensure_db()
    conn = get_connection()
    try:
        clauses: list[str] = []
        params: list[Any] = []
        if farmer_id:
            clauses.append("farmer_id = ?")
            params.append(farmer_id.strip())
        if status:
            clauses.append("UPPER(status) = ?")
            params.append(status.strip().upper())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(limit)
        rows = conn.execute(
            f"""
            SELECT id, farmer_id, title, message, crop, advisory_type, status,
                   created_at, updated_at, expires_at
            FROM advisories
            {where}
            ORDER BY id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_advisory_status(advisory_id: int, status: str) -> None:
    ensure_db()
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE advisories
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (status.strip().upper(), advisory_id),
        )
        conn.commit()
    finally:
        conn.close()


def recently_nudged(
    farmer_id: str,
    *,
    nudge_type: str = "rain_open_advisory",
    advisory_id: int | None = None,
    cooldown_hours: int = 24,
) -> bool:
    """True if a successfully delivered nudge of this type exists within cooldown."""
    ensure_db()
    conn = get_connection()
    try:
        if advisory_id is not None:
            row = conn.execute(
                """
                SELECT id FROM nudge_events
                WHERE farmer_id = ?
                  AND nudge_type = ?
                  AND advisory_id = ?
                  AND delivery_status = 'sent'
                  AND triggered_at >= datetime('now', ?)
                LIMIT 1
                """,
                (
                    farmer_id.strip(),
                    nudge_type,
                    advisory_id,
                    f"-{int(cooldown_hours)} hours",
                ),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT id FROM nudge_events
                WHERE farmer_id = ?
                  AND nudge_type = ?
                  AND delivery_status = 'sent'
                  AND triggered_at >= datetime('now', ?)
                LIMIT 1
                """,
                (
                    farmer_id.strip(),
                    nudge_type,
                    f"-{int(cooldown_hours)} hours",
                ),
            ).fetchone()
        return row is not None
    finally:
        conn.close()


def log_nudge_event(
    farmer_id: str,
    *,
    advisory_id: int | None,
    nudge_type: str,
    rain_detected: bool,
    forecast_window_hours: int,
    delivery_status: str,
    message_text: str | None = None,
    message_id: str | None = None,
    error: str | None = None,
    demo_mode: bool = False,
) -> int:
    ensure_db()
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO nudge_events (
                farmer_id, advisory_id, nudge_type, rain_detected,
                forecast_window_hours, delivery_status, message_text,
                message_id, error, demo_mode
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                farmer_id.strip(),
                advisory_id,
                nudge_type,
                1 if rain_detected else 0,
                forecast_window_hours,
                delivery_status,
                (message_text or "")[:2000] if message_text else None,
                message_id,
                (error or "")[:1000] if error else None,
                1 if demo_mode else 0,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def recent_nudge_events(
    limit: int = 50,
    farmer_id: str | None = None,
) -> list[dict[str, Any]]:
    ensure_db()
    conn = get_connection()
    try:
        if farmer_id:
            rows = conn.execute(
                """
                SELECT n.*, a.title AS advisory_title, a.crop AS advisory_crop
                FROM nudge_events n
                LEFT JOIN advisories a ON a.id = n.advisory_id
                WHERE n.farmer_id = ?
                ORDER BY n.id DESC
                LIMIT ?
                """,
                (farmer_id.strip(), limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT n.*, a.title AS advisory_title, a.crop AS advisory_crop
                FROM nudge_events n
                LEFT JOIN advisories a ON a.id = n.advisory_id
                ORDER BY n.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def start_proactive_run(*, demo_mode: bool = False, notes: str | None = None) -> int:
    ensure_db()
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO proactive_runs (demo_mode, notes)
            VALUES (?, ?)
            """,
            (1 if demo_mode else 0, notes),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def finish_proactive_run(
    run_id: int,
    *,
    farmers_checked: int,
    rain_detected_count: int,
    nudges_sent: int,
    failures: int,
    notes: str | None = None,
) -> None:
    ensure_db()
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE proactive_runs
            SET finished_at = datetime('now'),
                farmers_checked = ?,
                rain_detected_count = ?,
                nudges_sent = ?,
                failures = ?,
                notes = COALESCE(?, notes)
            WHERE id = ?
            """,
            (
                farmers_checked,
                rain_detected_count,
                nudges_sent,
                failures,
                notes,
                run_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def latest_proactive_run() -> dict[str, Any] | None:
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT * FROM proactive_runs
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def proactive_summary() -> dict[str, Any]:
    ensure_db()
    conn = get_connection()
    try:
        last = conn.execute(
            "SELECT * FROM proactive_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        sent = conn.execute(
            "SELECT COUNT(*) AS c FROM nudge_events WHERE delivery_status = 'sent'"
        ).fetchone()["c"]
        failed = conn.execute(
            "SELECT COUNT(*) AS c FROM nudge_events WHERE delivery_status = 'failed'"
        ).fetchone()["c"]
        open_count = conn.execute(
            "SELECT COUNT(*) AS c FROM advisories WHERE UPPER(status) = 'OPEN'"
        ).fetchone()["c"]
        return {
            "last_run": dict(last) if last else None,
            "total_nudges_sent": sent,
            "total_nudge_failures": failed,
            "open_advisories": open_count,
        }
    finally:
        conn.close()
