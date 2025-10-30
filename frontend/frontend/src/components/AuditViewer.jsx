// AuditViewer.jsx
import React, { useState, useEffect } from "react";
import { getAudits } from "../api";

export default function AuditViewer() {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const data = await getAudits("org123");
        if (mounted) setAudits(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to load audits:", err);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => { mounted = false; };
  }, []);

  if (loading) return <div className="card audit-card"><div className="audit-empty">Loading audits…</div></div>;

  return (
  <div className="card audit-card">
    {audits.length === 0 ? (
      <div className="audit-empty">
        No recent evaluations yet — run an expense test above to generate results.
      </div>
    ) : (
      <table className="audit-list" aria-label="Recent evaluations">
        <thead>
          <tr>
            <th>Expense</th>
            <th>Winning Rule</th>
            <th>Actions</th>
            <th>When</th>
          </tr>
        </thead>
        <tbody>
          {audits.map((a) => {
            let expense = {};
            let result = {};
                        try {
              expense =
                typeof a.expenseJson === "string"
                  ? JSON.parse(a.expenseJson)
                  : a.expenseJson || {};
            } catch {
              expense = {};
            }
            try {
              result =
                typeof a.resultJson === "string"
                  ? JSON.parse(a.resultJson)
                  : a.resultJson || {};
            } catch {
              result = {};
            }

            return (
              <tr key={a.id}>
                <td>{expense?.expense_id || "—"}</td>
                <td>{result?.winning_rule || "—"}</td>
                <td>{Array.isArray(result?.actions) && result.actions.length ? result.actions.join(", ") : "—"}</td>
                <td>{a.createdAt ? new Date(a.createdAt).toLocaleString() : "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    )}
  </div>
);

}
