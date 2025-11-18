# Jupiter AI Backend

Python FastAPI backend that powers the demo frontend located in `../demo_frontend`.  
This service exposes endpoints for authentication, email/document classification, response generation, and ERP synchronization.

## Getting started

1. Create a virtual environment and install dependencies:
   ```bash
   cd /Users/gwl/Desktop/demo/demo_backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
3. Open http://127.0.0.1:8000/docs to explore the OpenAPI docs.

## Environment variables

| Variable | Description | Default |
| --- | --- | --- |
| `FRONTEND_ORIGIN` | Allowed CORS origin | `*` |
| `JUPITER_SECRET_KEY` | Secret key for token signing | `change-this-dev-secret-key` |

## API summary

- `POST /auth/register` – email/password registration
- `POST /auth/login` – authenticate and obtain session token
- `POST /auth/google` – simplified OAuth-style login
- `GET /auth/session` – validate current session
- `POST /emails/classify` – classify subject/body text
- `POST /documents/analyze` – upload a document for extraction
- `POST /responses/generate` – produce AI-like responses
- `POST /erp/sync` – push structured data to ERP
- `GET /health` – health probe

All backend state lives in `data/app.db` (SQLite) and can be removed safely for a clean slate.


