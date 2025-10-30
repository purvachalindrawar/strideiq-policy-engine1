# DESIGN.md  
### StrideIQ Policy Engine – Architecture & Technical Design Document

---

## Overview

The **StrideIQ Policy Engine** is a backend-driven rule evaluation service that analyzes business expenses against a set of configurable policies.  
Each policy (rule) defines *conditions* and *actions*; when an expense is submitted, the engine evaluates all active rules, determines which rules match, and returns the resulting actions and evaluation trace.

The system is designed for clarity, modularity, and scalability — providing a strong backend foundation for a future React-based Admin UI.

---

## System Architecture

## System Architecture

```text
┌───────────────────────────────────────┐
│              React Frontend           │   (planned)
│  - Rule Editor & Tester               │
│  - Expense Evaluator UI               │
└───────────────────────────────────────┘
                  │
                  │ REST API
                  ▼
┌───────────────────────────────────────┐
│             FastAPI Backend            │
│   Endpoints: /policy/evaluate, /policy/audit  │
│                                           │
│   ┌─────────────────────────────────┐     │
│   │   Evaluation Engine (evaluate.py)│     │
│   │   - Condition parsing            │     │
│   │   - Rule precedence logic        │     │
│   │   - Trace & audit generation     │     │
│   └─────────────────────────────────┘     │
│                                           │
│   ┌─────────────────────────────────┐     │
│   │   Prisma Client (db_client.py)   │     │
│   │   - Rule & Audit models          │     │
│   │   - Async DB lifecycle           │     │
│   └─────────────────────────────────┘     │
└───────────────────────────────────────┘
                  │
                  ▼
┌───────────────────────────────────────┐
│          PostgreSQL Database          │
│  Tables: Rule, Audit                  │
│  Managed via Prisma (schema.prisma)   │
└───────────────────────────────────────┘

---

## Core Components

### **Rule Representation**

Each rule is represented as a Python model (Pydantic + Prisma):

```python
class Condition:
    field: str
    op: str
    value: Any
```
```python
class Rule:
    id: str
    name: str
    conditions: List[Condition]
    actions: List[str]
    active: bool
    priority: int

```
### **Evaluation Engine**
The evaluation engine processes incoming expense data against all active rules:
- **Input**: Expense JSON payload
- **Process**:
  - Load active rules from the database
  - For each rule, evaluate all conditions against the expense
  - Track which rules matched and their actions
  - Resolve conflicts based on rule priority
- **Output**: JSON response with matched actions and evaluation trace
### **Database Layer**
The database layer uses Prisma to define and manage the `Rule` and `Audit` models:
```prisma
model Rule {
  id          String   @id @default(cuid())
  name        String
  conditions  Json
  actions     Json
  active      Boolean  @default(true)
  priority    Int
  createdAt   DateTime @default(now())
  audits      Audit[]
}

model Audit {
  id          String   @id @default(cuid())
  orgId       String
  expenseJson Json
  resultJson  Json
  createdAt   DateTime @default(now())
  ruleId      String?
  rule        Rule?    @relation(fields: [ruleId], references: [id])
}

``` 
## Rule Precedence & Conflict Strategy

- **Primary Key:** `priority`  
- **Secondary Key:** `len(conditions)` → more specific rules win  
- If multiple rules share the same priority, the **first created** (based on timestamp) wins.  
- **Conflicting actions are not merged** — only the winning rule’s actions apply to maintain deterministic behavior.

---

## ⚡ Caching & Versioning (Future Scope)

Currently, rule retrieval happens via a Prisma query for each evaluation.  
For scaling and performance optimization, the following improvements can be implemented:

- **In-memory caching** using Redis or FastAPI background task refreshers.  
- **Versioning rules** by `createdAt` timestamp or an explicit version ID.  
- **Batch evaluation** for multiple expenses (vectorized rule checks) to improve throughput.

---

## 🚀 Scaling & Deployment Considerations

| **Area**                | **Design Decision** |
|--------------------------|---------------------|
| **Async IO**             | Entire stack (FastAPI + Prisma) is async for high concurrency |
| **Database Connections** | Reused via global Prisma client for efficient pooling |
| **Horizontal Scaling**   | Stateless API design; Prisma manages connection pooling across instances |
| **Containerization**     | Supports Docker and future docker-compose setup for seamless deployment |
| **Frontend Integration** | REST API endpoints designed for direct integration with React frontend |
| **Environment Variables**| Managed via `.env` file (secure, configurable per organization) |

---

## ⚖️ Tradeoffs & Limitations

- **No rule caching implemented** — intentionally omitted for prototype simplicity.  
- **No authentication layer** — will be added in future for multi-organization support.  
- **Rule conflicts** are resolved via fixed precedence rather than weighted scoring.  
- **Frontend not yet implemented** — planned for the next development iteration.

---

## 🧪 Testing Summary

| **Test Type** | **Description** |
|----------------|-----------------|
| **Unit** | Condition evaluation, rule precedence, and invalid input handling |
| **Integration** | Full database persistence tests via Prisma ORM |
| **API** | `/evaluate` and `/audit` endpoints tested using HTTPX |
| **Coverage** | 5+ scenarios — single match, no match, multi-match, order conflict, and missing input cases |
