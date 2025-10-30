# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import evaluate
from app.services.db_client import init_db, close_db

app = FastAPI(title="StrideIQ Policy Engine")

# Allow requests from the frontend dev server (Vite default) and local tools
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] for quick dev (less secure)
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # or ["*"]
    allow_headers=["*"],
)

# Register routes
app.include_router(evaluate.router)

# Optional: root endpoint...
@app.get("/", tags=["meta"])
async def root():
    return {
        "message": "StrideIQ Policy Engine (backend). See /docs for API documentation.",
        "endpoints": {
            "evaluate": "/orgs/{orgId}/policy/evaluate (POST)",
            "audit": "/orgs/{orgId}/policy/audit (GET)",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Lifecycle hooks
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()
