# MedSync

Project foundation for MedSync. This repository currently contains only the
base scaffolding — no medical functionality, authentication, database
models, or AI features have been implemented yet.

## Project structure

```
medsync/
├── frontend/          # Next.js + TypeScript + Tailwind CSS (App Router)
├── backend/           # FastAPI + Pydantic + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── main.py            # FastAPI app, GET /health
│   │   └── core/
│   │       ├── config.py      # Environment-based settings
│   │       └── database.py    # SQLAlchemy engine/session (no models yet)
│   ├── alembic/                # Migration scaffold (no revisions yet)
│   └── requirements.txt
├── .env.example        # Template for required environment variables
├── docker-compose.yml  # PostgreSQL service
└── README.md
```

## Prerequisites

- Node.js 20+
- Python 3.11+ (3.9+ works, 3.11+ recommended)
- Docker + Docker Compose

## 1. Configure environment variables

Copy the example env file and adjust values as needed:

```bash
cp .env.example .env
```

This file defines the PostgreSQL credentials, the backend port, and the
frontend's API URL. It is loaded by both `docker-compose.yml` and the
backend. Never commit your real `.env` file.

## 2. Start PostgreSQL

```bash
docker compose up -d
```

This starts a PostgreSQL 16 container on the port defined by
`POSTGRES_PORT` (default `5432`), using the credentials from `.env`.

## 3. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend reads its configuration (database URL, CORS origins, port)
from environment variables / `../.env` — see `app/core/config.py`.

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

## 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

## Notes

- No database models or migrations exist yet — Alembic is wired up
  (`backend/alembic/`) so future models can be migrated, but there is
  nothing to migrate at this stage.
- Secrets and credentials are never hardcoded; they are read from
  environment variables at runtime (see `.env.example`).
