"""Streamlit admin — recent conversations and diagnoses (Phase 4)."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Allow `streamlit run admin/streamlit_app.py` from project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import init_db
from app.services.repository import list_farmer_phones, recent_diagnoses, recent_messages

st.set_page_config(page_title="Smart Crop Bot Admin", page_icon="🌱", layout="wide")

init_db()

st.title("Smart Crop Bot — Admin")
st.caption("Phase 4 · read-only view of recent WhatsApp activity")

col_a, col_b = st.columns([2, 1])
with col_a:
    phone_filter = st.selectbox(
        "Filter by phone (optional)",
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

tab1, tab2 = st.tabs(["Conversations", "Diagnoses"])

with tab1:
    st.subheader("Recent messages")
    if not messages:
        st.info("No messages yet. Send a WhatsApp text/photo/voice to populate this.")
    else:
        st.dataframe(messages, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Recent crop diagnoses")
    if not diagnoses:
        st.info("No diagnoses yet. Send a crop leaf photo on WhatsApp.")
    else:
        st.dataframe(diagnoses, use_container_width=True, hide_index=True)

st.divider()
st.markdown(
    "DB file is configured via `DATABASE_PATH` in `.env` "
    "(default `data/smart_crop_bot.db`)."
)
