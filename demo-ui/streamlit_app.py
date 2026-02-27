import json
import os
from typing import Any

import requests
import streamlit as st

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 15


def _request(method: str, path: str, token: str | None = None, payload: dict | None = None) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method=method,
            url=f"{BACKEND_BASE_URL}{path}",
            headers=headers,
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )
        data = response.json()
        if response.status_code >= 400:
            return {"ok": False, "error": data.get("error", "Request failed"), "status": response.status_code}
        return {"ok": True, "data": data, "status": response.status_code}
    except requests.RequestException as exc:
        return {"ok": False, "error": str(exc), "status": 0}


st.set_page_config(page_title="Granite Demo (Streamlit)", layout="wide")
st.title("Granite AI Platform Demo (Streamlit)")
st.caption("This demo client calls backend-core-api endpoints only.")

if "token" not in st.session_state:
    st.session_state.token = ""

left, right = st.columns([1, 2])

with left:
    st.subheader("1) Login")
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", value="admin123!", type="password")
    if st.button("Login", use_container_width=True):
        result = _request("POST", "/auth/login", payload={"username": username, "password": password})
        if result["ok"]:
            st.session_state.token = result["data"]["access_token"]
            st.success("Login successful")
        else:
            st.error(result["error"])

    token_preview = st.session_state.token[:32] + "..." if st.session_state.token else "(not logged in)"
    st.code(token_preview, language="text")

with right:
    st.subheader("2) Inventory")
    if st.button("Get Inventory"):
        result = _request("GET", "/inventory", token=st.session_state.token)
        if result["ok"]:
            st.json(result["data"])
        else:
            st.error(result["error"])

st.divider()
c1, c2 = st.columns(2)

with c1:
    st.subheader("3) Create Hold")
    hold_inventory_id = st.number_input("Hold Inventory ID", min_value=1, value=1, step=1)
    hold_quantity = st.number_input("Hold Quantity", min_value=1, value=1, step=1)
    if st.button("Create Hold", use_container_width=True):
        result = _request(
            "POST",
            "/holds",
            token=st.session_state.token,
            payload={"inventory_id": int(hold_inventory_id), "quantity": int(hold_quantity)},
        )
        if result["ok"]:
            st.success("Hold created")
            st.json(result["data"])
        else:
            st.error(result["error"])

with c2:
    st.subheader("4) Draft + Approve Quote")
    quote_inventory_id = st.number_input("Quote Inventory ID", min_value=1, value=1, step=1)
    quote_quantity = st.number_input("Quote Quantity", min_value=1, value=1, step=1)
    if st.button("Draft Quote", use_container_width=True):
        result = _request(
            "POST",
            "/quotes/draft",
            token=st.session_state.token,
            payload={"inventory_id": int(quote_inventory_id), "quantity": int(quote_quantity)},
        )
        if result["ok"]:
            st.success("Quote drafted")
            st.json(result["data"])
        else:
            st.error(result["error"])

    quote_id = st.number_input("Quote ID to Approve", min_value=1, value=1, step=1)
    if st.button("Approve Quote", use_container_width=True):
        result = _request(
            "POST",
            "/quotes/approve",
            token=st.session_state.token,
            payload={"quote_id": int(quote_id)},
        )
        if result["ok"]:
            st.success("Quote approved")
            st.json(result["data"])
        else:
            st.error(result["error"])

st.divider()
st.subheader("Demo Notes")
st.markdown(
    "- RBAC is enforced by backend middleware on every endpoint except `/auth/login` and `/health`.\n"
    "- All state-changing operations write audit logs (`holds`, `quote draft`, `quote approve`).\n"
    "- This UI is only a thin client; business logic lives in backend-core-api."
)
