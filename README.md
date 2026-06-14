# Finance Report — Float vs Decimal Money Bug (React + FastAPI + PostgreSQL)

A small finance reporting app: it aggregates expense line items into
per-department and grand totals (net, tax, gross) and reconciles the
report against the ledger. The starter version computes money with Python
floats, so per-line tax rounding drifts and the report fails to reconcile
by a few cents.

## Architecture

```
finance-report/
├── db/
│   ├── schema.sql   # departments, line_items (amounts as NUMERIC)
│   └── seed.py      # demo data incl. half-cent boundary amounts
├── server/          # FastAPI + psycopg2  (port 4000)
│   └── app/
│       ├── main.py
│       ├── db.py
│       ├── report_service.py        # ⚠️ float version (the bug)
│       └── report_service_fixed.py  # ✅ Decimal version
└── client/          # React + Vite     (port 5173)
    └── src/App.jsx  # report table + reconciliation banner
```

## Requirements

- Python 3.10+, Node.js 18+, PostgreSQL 14+
  - macOS: `brew install python node postgresql@16`

## Setup

```bash
# 1. Database
createdb finance
PGUSER=postgres PGDATABASE=finance python3 db/seed.py

# 2. API
cd server
pip install -r requirements.txt
PGUSER=postgres PGDATABASE=finance ./run.sh        # http://localhost:4000

# 3. Client (another terminal)
cd client
npm install && npm run dev                          # http://localhost:5173
```

Open http://localhost:5173 — the reconciliation banner will show
**MISMATCH** with the starter (float) service.

## The bug, in one line

```python
>>> 2.05 * 1.10
2.2550000000000003   # wait, that's > 2.255, but round() still gives 2.25
>>> round(2.05 * 1.10, 2)
2.25                 # exact decimal answer is 2.26 — one cent lost per line
```

Switching `server/app/main.py` to import from `report_service_fixed`
(Decimal) makes the report reconcile exactly.
