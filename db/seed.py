#!/usr/bin/env python3
"""Seed the finance database with data that exposes float rounding error.

Run:  python db/seed.py   (with PG env vars set)

Two kinds of amounts are inserted:
  * "boundary" amounts whose 10% tax lands on a half-cent, where binary
    float rounds the wrong way vs exact decimal (e.g. 2.05 -> 2.255).
  * ordinary amounts, so the dataset looks realistic.

With enough boundary amounts, the per-line tax rounding done in float
drifts a visible number of cents away from the exact decimal total, and
the report fails to reconcile.
"""
import os
import psycopg2

DEPARTMENTS = [
    ("DEPT-OPS", "Operations"),
    ("DEPT-ENG", "Engineering"),
    ("DEPT-MKT", "Marketing"),
]

CATEGORIES = ["cloud", "travel", "software", "office", "training"]

# Net amounts whose 10% tax rounds differently in float vs Decimal.
# (Each ends in a half-cent after applying 10%.)
BOUNDARY = [
    "0.95", "1.15", "1.45", "1.65", "2.05", "3.05", "3.75", "4.55",
    "4.85", "5.35", "7.55", "7.85", "8.45", "8.75", "9.45", "10.35",
    "10.95", "11.95", "13.45", "16.95", "0.45", "0.55", "0.65", "0.85",
]

# Ordinary, non-boundary amounts to round out the dataset.
ORDINARY = [
    "12.00", "45.50", "120.00", "9.99", "33.33", "8.00", "250.00",
    "17.25", "60.40", "5.00",
]


def main():
    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
        dbname=os.environ.get("PGDATABASE", "finance"),
    )
    conn.autocommit = True
    cur = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
        cur.execute(f.read())
    print("Schema created.")

    dept_ids = []
    for code, name in DEPARTMENTS:
        cur.execute(
            "INSERT INTO departments (code, name) VALUES (%s, %s) RETURNING id",
            (code, name),
        )
        dept_ids.append(cur.fetchone()[0])
    print(f"Inserted {len(dept_ids)} departments.")

    total_items = 0
    for offset, dept_id in enumerate(dept_ids):
        # Each department gets all the boundary amounts (a few times) plus
        # the ordinary ones, so the rounding drift is clearly visible.
        amounts = BOUNDARY * 3 + ORDINARY
        for i, net in enumerate(amounts):
            ref = f"INV-2026-{dept_id:02d}{i:04d}"
            category = CATEGORIES[i % len(CATEGORIES)]
            cur.execute(
                """INSERT INTO line_items
                   (department_id, reference, category, net_amount, tax_rate)
                   VALUES (%s, %s, %s, %s, %s)""",
                (dept_id, ref, category, net, "0.1000"),
            )
            total_items += 1
    print(f"Inserted {total_items} line items.")

    cur.execute("SELECT COALESCE(SUM(net_amount), 0) FROM line_items")
    print("Exact net total (from DB NUMERIC):", cur.fetchone()[0])

    cur.close()
    conn.close()
    print("Seed complete.")


if __name__ == "__main__":
    main()
