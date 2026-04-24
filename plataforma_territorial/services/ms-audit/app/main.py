from fastapi import FastAPI
from app.routers import audit

app = FastAPI(title="Audit Service")

app.include_router(audit.router)

@app.get("/health")
def health():
    return {"status": "ok"}