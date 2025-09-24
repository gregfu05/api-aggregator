from fastapi import FastAPI
from app.api.routes_crypto import router as crypto_router

app = FastAPI(title="API Aggregator")
app.include_router(crypto_router)

@app.get("/health")
def health():
    return {"status": "ok"}
