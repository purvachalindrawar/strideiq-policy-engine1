// App.jsx
import React from "react";
import ExpenseTester from "./components/ExpenseTester";
import AuditViewer from "./components/AuditViewer";
import "./App.css";

export default function App() {
  return (
    <div className="page-wrap">
      <div className="container">
        <header className="site-header">
          <h1>StrideIQ Policy Engine</h1>
          <p className="subtitle">Admin prototype — evaluate expenses & view audits</p>
        </header>

        <main className="main-grid">
          <section className="panel left">
            <h2>Expense Policy Evaluator</h2>
            <ExpenseTester />
          </section>

          <aside className="panel right">
            <h2>Recent Evaluations</h2>
            <AuditViewer />
          </aside>
        </main>

        <footer className="footer">
          <small>Built by Kanon Chalindrawar • FastAPI + Prisma + PostgreSQL</small>
        </footer>
      </div>
    </div>
  );
}
