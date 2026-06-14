"""Report aggregation — STARTER VERSION (contains the float bug).

⚠️ This module computes monetary totals using Python floats. Every amount
read from the database is converted to float, gross (net + tax) is computed
in float, each line is rounded to cents, and the rounded values are summed.

Because values like 0.10 and the gross of 2.05 have no exact binary float
representation, the per-line rounding tips the wrong way on half-cent
boundaries, and the accumulated total drifts away from the exact decimal
figure. The report's own reconciliation check (sum of lines == grand total)
then fails by a few cents.

See report_service_fixed.py for the corrected version.
"""
from .db import get_conn


def _round2(x: float) -> float:
    # Round to cents the way the buggy code does — on a float.
    return round(x, 2)


def build_report():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """SELECT d.id, d.code, d.name
             FROM departments d
            ORDER BY d.code"""
    )
    departments = cur.fetchall()

    report = {"departments": [], "grandTotal": {}}

    grand_net = 0.0
    grand_tax = 0.0
    grand_gross = 0.0

    for dept_id, code, name in departments:
        cur.execute(
            """SELECT net_amount, tax_rate
                 FROM line_items
                WHERE department_id = %s
                ORDER BY id""",
            (dept_id,),
        )
        rows = cur.fetchall()

        dept_net = 0.0
        dept_tax = 0.0
        dept_gross = 0.0

        for net_amount, tax_rate in rows:
            # ⚠️ Convert exact decimals to float right away.
            net = float(net_amount)
            rate = float(tax_rate)

            tax = _round2(net * rate)      # per-line tax, rounded
            gross = _round2(net + tax)     # per-line gross, rounded

            dept_net = _round2(dept_net + net)
            dept_tax = _round2(dept_tax + tax)
            dept_gross = _round2(dept_gross + gross)

        report["departments"].append(
            {
                "code": code,
                "name": name,
                "lineCount": len(rows),
                "net": dept_net,
                "tax": dept_tax,
                "gross": dept_gross,
            }
        )

        grand_net = _round2(grand_net + dept_net)
        grand_tax = _round2(grand_tax + dept_tax)
        grand_gross = _round2(grand_gross + dept_gross)

    # Reconciliation against the LEDGER: the database can compute the exact
    # expected gross with SQL (NUMERIC arithmetic). The float-summed report
    # gross should match it to the cent — if it doesn't, the books don't
    # balance.
    cur.execute(
        """SELECT
              ROUND(SUM(net_amount), 2) AS net,
              ROUND(SUM(ROUND(net_amount * tax_rate, 2)), 2) AS tax,
              ROUND(SUM(net_amount + ROUND(net_amount * tax_rate, 2)), 2) AS gross
            FROM line_items"""
    )
    ledger = cur.fetchone()
    ledger_gross = float(ledger[2])
    reconciled = grand_gross == ledger_gross

    report["grandTotal"] = {
        "net": grand_net,
        "tax": grand_tax,
        "gross": grand_gross,
        "ledgerGross": ledger_gross,
        "reconciled": reconciled,
    }

    cur.close()
    conn.close()
    return report
