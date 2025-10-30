# backend/app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "policy-engine-backend"}

from app.routes import evaluate
app.include_router(evaluate.router)
