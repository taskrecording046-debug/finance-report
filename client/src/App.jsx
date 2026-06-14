import { useEffect, useState } from "react";
import { api } from "./api/client";

// Format a money value (string or number) for display.
function money(v) {
  return Number(v).toLocaleString("en", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export default function App() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getReport().then(setReport).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="state error">{error}</div>;
  if (!report) return <div className="state">Loading report…</div>;

  const g = report.grandTotal;

  return (
    <div className="page">
      <header className="head">
        <p className="eyebrow">FINANCE · QUARTERLY ROLLUP</p>
        <h1>Expense Report</h1>
      </header>

      <table className="report">
        <thead>
          <tr>
            <th>Department</th>
            <th className="num">Lines</th>
            <th className="num">Net</th>
            <th className="num">Tax</th>
            <th className="num">Gross</th>
          </tr>
        </thead>
        <tbody>
          {report.departments.map((d) => (
            <tr key={d.code}>
              <td>
                <span className="code">{d.code}</span> {d.name}
              </td>
              <td className="num">{d.lineCount}</td>
              <td className="num">{money(d.net)}</td>
              <td className="num">{money(d.tax)}</td>
              <td className="num">{money(d.gross)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td>Grand total</td>
            <td className="num"></td>
            <td className="num">{money(g.net)}</td>
            <td className="num">{money(g.tax)}</td>
            <td className="num strong">{money(g.gross)}</td>
          </tr>
        </tfoot>
      </table>

      <div className={`recon ${g.reconciled ? "ok" : "fail"}`}>
        <span className="recon-label">Reconciliation</span>
        <span className="recon-detail">
          report gross = {money(g.gross)} vs ledger = {money(g.ledgerGross)} —{" "}
          {g.reconciled ? "balanced" : "MISMATCH"}
        </span>
      </div>
    </div>
  );
}
