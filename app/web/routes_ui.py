
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.aggregator import aggregate_with_cache

router = APIRouter()
templates = Jinja2Templates(directory="templates")
templates.env.auto_reload = True  # helps during dev

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "symbols": "",
            "result": None,
            "error": None,
            "title": "CryptoStock – Mixed",
            "active": "mixed",
        },
    )

@router.get("/ui/search", response_class=HTMLResponse)
def ui_search(
    request: Request,
    symbols: str = Query("", description="CSV e.g. bitcoin,AAPL"),
    window: int = Query(60, description="Cache TTL seconds"),
):
    ctx = {
        "request": request,
        "symbols": symbols,
        "title": "CryptoStock – Mixed",
        "active": "mixed",
    }
    if not symbols.strip():
        return templates.TemplateResponse(
            "index.html", {**ctx, "result": None, "error": "Please enter at least one symbol."}
        )
    try:
        data = aggregate_with_cache(symbols, window=window)
        return templates.TemplateResponse("index.html", {**ctx, "result": data, "error": None})
    except Exception as e:
        return templates.TemplateResponse("index.html", {**ctx, "result": None, "error": str(e)})
