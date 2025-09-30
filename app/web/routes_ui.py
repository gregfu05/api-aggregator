from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.aggregator import aggregate as do_aggregate

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "symbols": "",
            "result": None,
            "error": None,
            "title": "API Aggregator – Mixed",
            "active": "mixed",   
        },
    )
@router.get("/ui/search", response_class=HTMLResponse)
def ui_search(request: Request, symbols: str = Query("", description="CSV e.g. bitcoin,AAPL"), window: int = Query(60)):
    if not symbols.strip():
        return templates.TemplateResponse("index.html", {"request": request, "symbols": symbols, "result": None, "error": "Please enter at least one symbol."})
    try:
        data = do_aggregate(symbols)
        return templates.TemplateResponse("index.html", {"request": request, "symbols": symbols, "result": data, "error": None})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "symbols": symbols, "result": None, "error": str(e)})
