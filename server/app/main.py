"""Finance reporting API.

GET /api/report  — per-department and grand totals (net, tax, gross) with
a reconciliation flag.
GET /api/line-items?department=CODE  — raw line items for drill-down.
GET /api/health
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .report_service import build_report
from .db import get_conn

app = FastAPI(title="Finance Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/report")
def report():
    return build_report()


@app.get("/api/line-items")
def line_items(department: str | None = None):
    conn = get_conn()
    cur = conn.cursor()
    if department:
        cur.execute(
            """SELECT li.reference, li.category, li.net_amount, li.tax_rate
                 FROM line_items li
                 JOIN departments d ON d.id = li.department_id
                WHERE d.code = %s
                ORDER BY li.id
                LIMIT 200""",
            (department,),
        )
    else:
        cur.execute(
            """SELECT reference, category, net_amount, tax_rate
                 FROM line_items
                ORDER BY id
                LIMIT 200"""
        )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {
        "items": [
            {
                "reference": r[0],
                "category": r[1],
                "netAmount": str(r[2]),
                "taxRate": str(r[3]),
            }
            for r in rows
        ]
    }
