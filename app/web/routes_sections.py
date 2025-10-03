
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.aggregator import aggregate_with_cache

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/crypto", response_class=HTMLResponse)
def crypto_page(request: Request, symbol: str = Query("")):
    result = None
    error = None
    if symbol.strip():
        try:
            result = aggregate_with_cache(symbol, window=60)
        except Exception as e:
            error = str(e)
    return templates.TemplateResponse(
        "crypto.html",
        {
            "request": request,
            "symbol": symbol,
            "result": result,
            "error": error,
            "title": "CryptoStock – Crypto",
            "active": "crypto",
        },
    )

@router.get("/stocks", response_class=HTMLResponse)
def stocks_page(request: Request, symbol: str = Query("")):
    result = None
    error = None
    if symbol.strip():
        try:
            result = aggregate_with_cache(symbol, window=60)
        except Exception as e:
            error = str(e)
    return templates.TemplateResponse(
        "stocks.html",
        {
            "request": request,
            "symbol": symbol,
            "result": result,
            "error": error,
            "title": "CryptoStock – Stocks",
            "active": "stocks",
        },
    )
