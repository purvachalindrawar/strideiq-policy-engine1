# 🧠 StrideIQ Policy Engine

A prototype **Policy Engine** built as part of the StrideIQ Challenge.

This project implements a **rule-based policy evaluation system** that analyzes business expenses and determines outcomes such as *flag*, *reject*, or *require approval*.  
It is designed as a modular backend (FastAPI + Prisma + PostgreSQL) with planned frontend support (React) for an Admin UI.

---

## ⚙️ Tech Stack

| Layer | Technology |
|--------|-------------|
| Frontend | React (planned) |
| Backend | FastAPI (Python 3.12) |
| ORM | Prisma (Python Client) |
| Database | PostgreSQL (Docker) |
| Testing | Pytest, HTTPX |
| Environment | Windows (PowerShell / CMD) |
| Version Control | Git + GitHub |

---

## 🚀 Features

✅ **Backend API**
- Evaluate expenses against policy rules  
- Rule precedence and conflict resolution  
- Rule persistence in PostgreSQL (via Prisma)  
- Audit logging for all evaluations  
- REST endpoints for evaluation and audit retrieval  

✅ **Database (Prisma + Postgres)**
- `Rule` and `Audit` models  
- Schema managed via Prisma migrations  
- Seed script to populate sample rules  

✅ **Testing**
- Unit tests for rule evaluation logic  
- Integration tests verifying full DB persistence and audit flow  

✅ **Scalable Design**
- Modular FastAPI structure (`routes/`, `services/`, `prisma_data/`)  
- Async Prisma client lifecycle managed on startup/shutdown  
- Future-ready for React Admin UI integration  

---

## 🗂️ Directory Structure

```bash
strideiq-policy-engine/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── evaluate.py              # Core rule evaluation API
│   │   ├── services/
│   │   │   └── db_client.py             # Prisma DB connection & helpers
│   │   └── main.py                      # FastAPI entrypoint
│   │
│   ├── prisma_data/
│   │   └── schema.prisma                # Prisma schema (Rule & Audit models)
│   │
│   ├── tests/
│   │   ├── test_policy_engine.py        # Unit tests
│   │   └── test_db_integration.py       # Integration test (DB persistence)
│   │
│   ├── .env.example                     # Sample DATABASE_URL config
│   └── requirements.txt
│
├── frontend/                            # (Planned React Admin UI)
│
├── pytest.ini                           # Pytest configuration
├── DESIGN.md                            # Architecture & design notes
└── README.md                            # (This file)

---

## 🧩 Backend Setup (Windows / PowerShell)

### Clone the repository
```powershell
git clone https://github.com/<your-username>/strideiq-policy-engine.git
cd strideiq-policy-engine
```

### Create and activate virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### Install dependencies
```powershell
pip install -r backend/requirements.txt
```

### Start PostgreSQL via Docker
```powershell
docker run --name strideiq-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=Purv@19205 -e POSTGRES_DB=strideiq -p 5432:5432 -d postgres
```

### Set the environment variable
```powershell
$env:DATABASE_URL = "postgresql://postgres:Purv%4019205@localhost:5432/strideiq"
```

### Run Prisma migrations and seed data
```powershell
cd backend
prisma migrate dev --name init_schema --schema prisma_data/schema.prisma
python prisma/seed.py
cd ..

```

### Start the FastAPI server
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000 --app-dir backend
```

### Server runs at:

```bash
http://127.0.0.1:8000
```

---

## API Endpoints

### **POST** `/orgs/{orgId}/policy/evaluate`
Evaluates an expense JSON object against all active rules.

#### Example Request
```json
{
  "expense_id": "exp_1",
  "amount": 350,
  "category": "Food",
  "working_hours": 13,
  "employee_id": "u_123"
}

### Example Response
```json
{
  "matched_rules": ["r2"],
  "winning_rule": "r2",
  "actions": ["flag"],
  "trace": [
    {"rule": "r1", "matched": false, "reason": "amount>5000:false"},
    {"rule": "r2", "matched": true, "reason": "amount>200 && working_hours>12:true"}
  ]
}

```

## Running Tests
```powershell
python -m pytest -v
```

### Example Output
```powershell
collected 5 items
backend/tests/test_policy_engine.py::PASSED
backend/tests/test_db_integration.py::PASSED
```

---

## 🎨 Frontend (Planned)

The React frontend (to be added) will provide:

- **Rule List + Editor (CRUD)** – Create, read, update, and delete policy rules.  
- **Rule Reordering (Drag & Drop)** – Adjust rule priority visually.  
- **“Test Expense” Form** – Interactively test expenses by sending data to the backend `/evaluate` endpoint.  
- **Audit Viewer** – Display recent evaluations by fetching data from the `/audit` endpoint.

> 🧱 The `frontend/` folder is already pre-created and reserved for this phase.

---

## 🚀 Future Enhancements

- **Add caching and rule versioning** – Improve performance and maintain rule history.  
- **Add authentication and org-level rule management** – Secure multi-tenant support.  
- **Add real-time audit dashboard** – Visualize evaluations and rule hits live.  
- **Containerize full stack with docker-compose** – Simplify deployment and local setup.  
- **Build frontend React prototype (in progress)** – Develop the planned interactive UI.


## 👩‍💻 Author

**Purva Chalindrawar**  
*Full Stack Developer | FastAPI • Prisma • PostgreSQL • React*


---

## 🧾 License

This project was built as part of the **StrideIQ Policy Engine Challenge (Prototype)**.  
Use of this codebase is intended for **demonstration and learning purposes** only.
