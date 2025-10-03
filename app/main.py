from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.routes_crypto import router as crypto_router
from app.api.routes_stocks import router as stocks_router
from app.api.routes_aggregate import router as aggregate_router
from app.api.routes_cache import router as cache_router 
from app.core.request_logging import request_logger_mw
from app.api.routes_logs import router as logs_router
from app.web.routes_ui import router as ui_router
from app.api.routes_assets import router as assets_router
from app.api.routes_suggest import router as suggest_router
from app.web.routes_sections import router as sections_router
from app.api.routes_history import router as history_router

app = FastAPI(title="API Aggregator")
app.include_router(crypto_router)
app.include_router(stocks_router)
app.include_router(aggregate_router)
app.include_router(cache_router)    
app.middleware("http")(request_logger_mw) 
app.include_router(logs_router)   
app.include_router(ui_router)
app.include_router(assets_router)
app.include_router(suggest_router)
app.include_router(sections_router)
app.include_router(history_router)

@app.get("/health")
def health():
    return {"status": "ok"}
