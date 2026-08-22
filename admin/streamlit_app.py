"""Streamlit admin — conversations, diagnoses, proactive nudges."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Allow `streamlit run admin/streamlit_app.py` from project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.db import init_db
from app.services.repository import (
    list_advisories,
    list_farmer_phones,
    proactive_summary,
    recent_diagnoses,
    recent_messages,
    recent_nudge_events,
)

st.set_page_config(page_title="Smart Crop Bot Admin", page_icon="🌱", layout="wide")

init_db()
settings = get_settings()

st.title("Smart Crop Bot — Admin")
st.caption("Phase 4–5 · Telegram activity + proactive nudges")

col_a, col_b = st.columns([2, 1])
with col_a:
    phone_filter = st.selectbox(
        "Filter by farmer id (optional)",
        options=["(all)"] + list_farmer_phones(),
    )
with col_b:
    limit = st.slider("Rows", min_value=10, max_value=200, value=50, step=10)
    refresh = st.button("Refresh", type="primary")

phone = None if phone_filter == "(all)" else phone_filter

if refresh:
    st.rerun()

messages = recent_messages(limit=limit, phone=phone)
diagnoses = recent_diagnoses(limit=limit, phone=phone)
nudges = recent_nudge_events(limit=limit, farmer_id=phone)
advisories = list_advisories(farmer_id=phone, limit=limit)
summary = proactive_summary()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Conversations", "Diagnoses", "Proactive Nudges", "Advisories"]
)

with tab1:
    st.subheader("Recent messages")
    if not messages:
        st.info("No messages yet. Send a Telegram text/photo/voice to populate this.")
    else:
        st.dataframe(messages, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Recent crop diagnoses")
    if not diagnoses:
        st.info("No diagnoses yet. Send a crop leaf photo on Telegram.")
    else:
        st.dataframe(diagnoses, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Proactive status")
    last = summary.get("last_run") or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Proactive enabled", str(settings.proactive_enabled))
    c2.metric("Interval (min)", settings.proactive_check_interval_minutes)
    c3.metric("Nudges sent (all-time)", summary.get("total_nudges_sent", 0))
    c4.metric("Nudge failures (all-time)", summary.get("total_nudge_failures", 0))

    st.markdown(
        f"- Demo mode setting: `{settings.proactive_demo_mode}`  \n"
        f"- Open advisories: `{summary.get('open_advisories', 0)}`  \n"
        f"- Last run started: `{last.get('started_at', '—')}`  \n"
        f"- Last run finished: `{last.get('finished_at', '—')}`  \n"
        f"- Last farmers checked: `{last.get('farmers_checked', '—')}`  \n"
        f"- Last rain detections: `{last.get('rain_detected_count', '—')}`  \n"
        f"- Last nudges sent: `{last.get('nudges_sent', '—')}`  \n"
        f"- Last failures: `{last.get('failures', '—')}`"
    )

    st.subheader("Recent nudge events")
    if not nudges:
        st.info(
            "No proactive nudges yet. Seed an OPEN advisory, ensure location, "
            "then run `scripts/test_proactive.py`."
        )
    else:
        st.dataframe(nudges, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Advisories")
    if not advisories:
        st.info("No advisories. Use `scripts/seed_advisory.py --farmer-id telegram:...`")
    else:
        st.dataframe(advisories, use_container_width=True, hide_index=True)

st.divider()
st.markdown(
    "DB file is configured via `DATABASE_PATH` in `.env` "
    "(default `data/smart_crop_bot.db`)."
)
