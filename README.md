# Dynamic Pricing System

A full-stack demo that **dynamically adjusts service prices based on the number of active users**. Built for an engineering student portfolio with a real database, REST API, and modern frontend.

## Architecture

```
┌─────────────────┐     REST API      ┌──────────────────────┐
│  React frontend │ ◄──────────────► │  FastAPI backend      │
│  (Vite, port    │                   │  (port 8000)         │
│   5173)         │                   └──────────┬───────────┘
└─────────────────┘                              │
                                                 ▼
                                      ┌──────────────────────┐
                                      │  SQLite (pricing.db) │
                                      │  - pricing_config    │
                                      │  - pricing_tiers     │
                                      │  - active_users      │
                                      └──────────────────────┘
```

## Pricing modes

| Mode | Formula |
|------|---------|
| **Tiered** | Price is selected from configured user-count bands (e.g. 0–50 → $9.99) |
| **Linear** | `price = base_price + (active_users × per_user_rate)` |

Switch modes and edit tiers from the **Admin config** tab.

## Quick start

### Option A — Single server (no Node.js required)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000 — the React UI is served as static files from the same server.

### Option B — Vite dev server (requires Node.js)

```bash
# Terminal 1 — backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard` | Active users, current price, config |
| GET | `/api/price` | Current computed price |
| POST | `/api/users` | Join service (creates active user) |
| POST | `/api/users/{id}/leave` | Mark user inactive |
| GET/PATCH | `/api/admin/config` | Read/update pricing config |
| CRUD | `/api/admin/tiers` | Manage pricing tiers |

## How to demo

1. Start backend and frontend.
2. On the **Live dashboard**, join the service with a name — price updates as active users increase.
3. Open another browser tab (or incognito) and join again to simulate more users.
4. Switch to **Admin config** to change tiers or switch to linear pricing.
5. Watch the live price recalculate automatically every 5 seconds.

## Project structure

```
dynamic-pricing-system/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + seed data
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── pricing.py       # Pricing engine
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── routes/          # API routes
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx          # Dashboard + admin UI
        └── api.js           # API client
```

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, Pydantic
- **Frontend:** React 18, Vite
- **Database:** SQLite (file-based, zero setup)
