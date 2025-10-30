from fastapi import FastAPI
from app.routes import evaluate
from app.services.db_client import init_db, close_db

app = FastAPI(title="StrideIQ Policy Engine")

# Register routes
app.include_router(evaluate.router)

# Handle DB lifecycle
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()
