from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.aggregator import aggregate as do_aggregate

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/crypto", response_class=HTMLResponse)
def crypto_page(request: Request, symbol: str = Query("")):
    result = error = None
    if symbol.strip():
        try: result = do_aggregate(symbol)
        except Exception as e: error = str(e)
    return templates.TemplateResponse(
        "crypto.html",
        {
            "request": request,
            "symbol": symbol,
            "result": result,
            "error": error,
            "title": "API Aggregator – Crypto",
            "active": "crypto",  # <-- add this
        },
    )

@router.get("/stocks", response_class=HTMLResponse)
def stocks_page(request: Request, symbol: str = Query("")):
    result = error = None
    if symbol.strip():
        try: result = do_aggregate(symbol)
        except Exception as e: error = str(e)
    return templates.TemplateResponse(
        "stocks.html",
        {
            "request": request,
            "symbol": symbol,
            "result": result,
            "error": error,
            "title": "API Aggregator – Stocks",
            "active": "stocks",  # <-- add this
        },
    )
