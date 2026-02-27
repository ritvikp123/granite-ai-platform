# Demo UI (Gradio + Streamlit)

This folder contains two lightweight frontend demos for `backend-core-api`.

- `gradio_app.py` for a quick interactive demo UI
- `streamlit_app.py` for a dashboard-style demo UI

## 1) Start Backend

From repo root:

```powershell
cd backend-core-api
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Backend default URL: `http://127.0.0.1:8000`

## 2) Start Demo UI Environment

Open another terminal from repo root:

```powershell
cd demo-ui
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional backend URL override:

```powershell
$env:BACKEND_BASE_URL="http://127.0.0.1:8000"
```

## 3) Run Gradio

```powershell
python gradio_app.py
```

Open: `http://127.0.0.1:7860`

## 4) Run Streamlit

```powershell
streamlit run streamlit_app.py
```

Open: `http://localhost:8501`

## Default Login

- Username: `admin`
- Password: `admin123!`

## Endpoints Used

- `POST /auth/login`
- `GET /inventory`
- `POST /holds`
- `POST /quotes/draft`
- `POST /quotes/approve`
