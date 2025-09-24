from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.routes_crypto import router as crypto_router
from app.api.routes_stocks import router as stocks_router
from app.api.routes_aggregate import router as aggregate_router

app = FastAPI(title="API Aggregator")
app.include_router(crypto_router)
app.include_router(stocks_router)
app.include_router(aggregate_router)

@app.get("/health")
def health():
    return {"status": "ok"}
