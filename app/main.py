from fastapi import FastAPI
from app.api.v1.endpoints import data

app: FastAPI = FastAPI(
    title="Backtester2.0",
    version="1.0.0",
)

# Register API routers
app.include_router(router=data.router, prefix="/api/v1")


@app.get("/")
def health_check():
  return {"status": "online", "engine": "DuckDB + FastAPI"}