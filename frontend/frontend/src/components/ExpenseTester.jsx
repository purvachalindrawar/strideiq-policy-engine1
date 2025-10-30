// ExpenseTester.jsx
import React, { useState } from "react";
import { evaluateExpense } from "../api";

export default function ExpenseTester() {
  const [expense, setExpense] = useState({
    expense_id: "",
    amount: "",
    category: "",
    working_hours: "",
    employee_id: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onChange = (e) => {
    const { name, value } = e.target;
    setExpense((s) => ({ ...s, [name]: value }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!expense.expense_id) {
      setError("Expense ID is required.");
      return;
    }

    setLoading(true);
    try {
      const data = await evaluateExpense("org123", {
        ...expense,
        amount: expense.amount !== "" ? Number(expense.amount) : undefined,
        working_hours: expense.working_hours !== "" ? Number(expense.working_hours) : undefined,
      });
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("Unable to evaluate — check backend or proxy.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <form onSubmit={onSubmit}>
        <div className="form-row">
          <label>Expense ID</label>
          <input className="input" name="expense_id" placeholder="exp_1" value={expense.expense_id} onChange={onChange} />
        </div>

        <div className="form-row">
          <label>Amount</label>
          <input className="input" name="amount" placeholder="e.g. 350" value={expense.amount} onChange={onChange} />
        </div>

        <div className="form-row">
          <label>Category</label>
          <input className="input" name="category" placeholder="Food" value={expense.category} onChange={onChange} />
        </div>

        <div className="form-row">
          <label>Working Hours</label>
          <input className="input" name="working_hours" placeholder="e.g. 12" value={expense.working_hours} onChange={onChange} />
        </div>

        <div className="form-row">
          <label>Employee ID</label>
          <input className="input" name="employee_id" placeholder="emp_101" value={expense.employee_id} onChange={onChange} />
        </div>

        <button className="btn" type="submit" disabled={loading}>
          {loading ? "Evaluating..." : "Run Evaluation"}
        </button>
      </form>

      {error && <div className="result-card" style={{ background: "#fff3f3", color: "var(--danger)" }}>{error}</div>}

      {result && (
        <div className="result-card">
          <h3>Result</h3>
          <div className="result-item"><strong>Matched Rules:</strong> {result.matched_rules?.length ? result.matched_rules.join(", ") : "—"}</div>
          <div className="result-item"><strong>Winning Rule:</strong> {result.winning_rule || "—"}</div>
          <div className="result-item"><strong>Actions:</strong> {result.actions?.length ? result.actions.join(", ") : "—"}</div>
          <div style={{ marginTop: 8 }}>
            <h4 style={{ margin: "6px 0" }}>Trace</h4>
            <ul>
              {result.trace?.map((t, i) => <li key={i}>{t.rule}: {t.reason}</li>)}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
