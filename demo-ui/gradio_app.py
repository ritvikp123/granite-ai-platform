import json
import os
from typing import Any

import gradio as gr
import requests

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 15


def _pretty(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def login(username: str, password: str) -> tuple[str, str]:
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=TIMEOUT_SECONDS,
        )
        data = response.json()
        if response.status_code >= 400:
            return "", f"Login failed: {data.get('error', 'Unknown error')}"
        return data["access_token"], "Login successful."
    except requests.RequestException as exc:
        return "", f"Connection error: {exc}"


def get_inventory(token: str) -> str:
    if not token:
        return "Please login first."
    try:
        response = requests.get(
            f"{BACKEND_BASE_URL}/inventory",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT_SECONDS,
        )
        data = response.json()
        if response.status_code >= 400:
            return _pretty({"error": data.get("error", "Request failed")})
        return _pretty(data)
    except requests.RequestException as exc:
        return _pretty({"error": str(exc)})


def create_hold(token: str, inventory_id: int, quantity: int) -> str:
    if not token:
        return "Please login first."
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/holds",
            headers={"Authorization": f"Bearer {token}"},
            json={"inventory_id": inventory_id, "quantity": quantity},
            timeout=TIMEOUT_SECONDS,
        )
        data = response.json()
        if response.status_code >= 400:
            return _pretty({"error": data.get("error", "Request failed")})
        return _pretty(data)
    except requests.RequestException as exc:
        return _pretty({"error": str(exc)})


def draft_quote(token: str, inventory_id: int, quantity: int) -> str:
    if not token:
        return "Please login first."
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/quotes/draft",
            headers={"Authorization": f"Bearer {token}"},
            json={"inventory_id": inventory_id, "quantity": quantity},
            timeout=TIMEOUT_SECONDS,
        )
        data = response.json()
        if response.status_code >= 400:
            return _pretty({"error": data.get("error", "Request failed")})
        return _pretty(data)
    except requests.RequestException as exc:
        return _pretty({"error": str(exc)})


def approve_quote(token: str, quote_id: int) -> str:
    if not token:
        return "Please login first."
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/quotes/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"quote_id": quote_id},
            timeout=TIMEOUT_SECONDS,
        )
        data = response.json()
        if response.status_code >= 400:
            return _pretty({"error": data.get("error", "Request failed")})
        return _pretty(data)
    except requests.RequestException as exc:
        return _pretty({"error": str(exc)})


with gr.Blocks(title="Granite AI Platform Demo (Gradio)") as app:
    gr.Markdown("# Granite AI Platform Demo (Gradio)")
    gr.Markdown(
        "This UI talks to backend-core-api only. "
        "No model runtime logic is implemented here."
    )

    token_state = gr.State("")

    with gr.Row():
        username = gr.Textbox(label="Username", value="admin")
        password = gr.Textbox(label="Password", value="admin123!", type="password")
        login_button = gr.Button("Login")
    login_status = gr.Textbox(label="Login Status")
    token_preview = gr.Textbox(label="JWT Token (preview)", interactive=False)

    login_button.click(
        fn=login,
        inputs=[username, password],
        outputs=[token_state, login_status],
    ).then(fn=lambda t: t[:32] + "..." if t else "", inputs=token_state, outputs=token_preview)

    with gr.Row():
        inventory_button = gr.Button("Get Inventory")
    inventory_output = gr.Code(label="Inventory Response", language="json")
    inventory_button.click(fn=get_inventory, inputs=token_state, outputs=inventory_output)

    with gr.Row():
        hold_inventory_id = gr.Number(label="Hold: Inventory ID", value=1, precision=0)
        hold_quantity = gr.Number(label="Hold: Quantity", value=1, precision=0)
        hold_button = gr.Button("Create Hold")
    hold_output = gr.Code(label="Hold Response", language="json")
    hold_button.click(
        fn=lambda token, iid, qty: create_hold(token, int(iid), int(qty)),
        inputs=[token_state, hold_inventory_id, hold_quantity],
        outputs=hold_output,
    )

    with gr.Row():
        quote_inventory_id = gr.Number(label="Draft Quote: Inventory ID", value=1, precision=0)
        quote_quantity = gr.Number(label="Draft Quote: Quantity", value=1, precision=0)
        draft_button = gr.Button("Draft Quote")
    draft_output = gr.Code(label="Quote Draft Response", language="json")
    draft_button.click(
        fn=lambda token, iid, qty: draft_quote(token, int(iid), int(qty)),
        inputs=[token_state, quote_inventory_id, quote_quantity],
        outputs=draft_output,
    )

    with gr.Row():
        approve_quote_id = gr.Number(label="Approve Quote: Quote ID", value=1, precision=0)
        approve_button = gr.Button("Approve Quote")
    approve_output = gr.Code(label="Quote Approve Response", language="json")
    approve_button.click(
        fn=lambda token, qid: approve_quote(token, int(qid)),
        inputs=[token_state, approve_quote_id],
        outputs=approve_output,
    )


if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860)
