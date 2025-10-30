# backend/app/main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok", "service": "policy-engine-backend"}

from app.routes import evaluate
app.include_router(evaluate.router)


from app.services.db_client import init_db, close_db

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.on_event("shutdown")
async def on_shutdown():
    await close_db()

