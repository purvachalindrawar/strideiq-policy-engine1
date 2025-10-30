from fastapi import FastAPI
from app.routes import evaluate
from app.services.db_client import init_db, close_db

app = FastAPI(title="StrideIQ Policy Engine")

# Register routes
app.include_router(evaluate.router)

# helpful root
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

# Lifecycle hooks (keep what you already have)
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()
