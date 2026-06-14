from .db import get_conn
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

def _round2(x: Decimal) -> Decimal:
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


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
    grand_net = grand_tax = grand_gross = Decimal("0")

    for dept_id, code, name in departments:
        cur.execute(
            """SELECT net_amount, tax_rate
                 FROM line_items
                WHERE department_id = %s
                ORDER BY id""",
            (dept_id,),
        )
        rows = cur.fetchall()

        dept_net = dept_tax = dept_gross = Decimal("0")

        for net_amount, tax_rate in rows:
            net = net_amount
            rate = tax_rate

            tax = _round2(net * rate)    
            gross = _round2(net + tax)  

            dept_net += net
            dept_tax += tax
            dept_gross += gross

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
