"""Phase 5 resilience helpers — dedupe + simple per-phone rate limit."""

from __future__ import annotations

import logging
import threading
import time
from collections import deque

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_seen_sids: dict[str, float] = {}
_phone_hits: dict[str, deque[float]] = {}

# Keep SID memory for 10 minutes
_SID_TTL_SEC = 600
# Max messages per phone in a rolling window
_RATE_LIMIT_COUNT = 20
_RATE_LIMIT_WINDOW_SEC = 60


def _prune_sids(now: float) -> None:
    expired = [k for k, ts in _seen_sids.items() if now - ts > _SID_TTL_SEC]
    for k in expired:
        _seen_sids.pop(k, None)


def is_duplicate_message(message_id: str | None) -> bool:
    """Return True if this message id was already processed recently."""
    if not message_id:
        return False
    now = time.time()
    with _lock:
        _prune_sids(now)
        if message_id in _seen_sids:
            logger.warning("Duplicate message id ignored: %s", message_id)
            return True
        _seen_sids[message_id] = now
        return False


def is_rate_limited(phone: str | None) -> bool:
    """Simple in-memory rate limit to protect free-tier demos."""
    if not phone:
        return False
    now = time.time()
    with _lock:
        q = _phone_hits.setdefault(phone, deque())
        while q and now - q[0] > _RATE_LIMIT_WINDOW_SEC:
            q.popleft()
        if len(q) >= _RATE_LIMIT_COUNT:
            logger.warning("Rate limit hit for %s (%s/%ss)", phone, len(q), _RATE_LIMIT_WINDOW_SEC)
            return True
        q.append(now)
        return False


RATE_LIMIT_REPLY_HI = (
    "बहुत सारे संदेश आ गए। कृपया एक मिनट बाद फिर कोशिश करें।"
)
