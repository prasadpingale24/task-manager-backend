from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="Task Manager API",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(api_router, prefix="/api/v1")
