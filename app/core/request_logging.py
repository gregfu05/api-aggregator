import time
from typing import Callable
from fastapi import Request
from starlette.responses import Response
from app.db.mongo import get_db

async def request_logger_mw(request: Request, call_next: Callable):
    start = time.perf_counter()
    status = 500  # default status if response fails
    try:
        response: Response = await call_next(request)
        status = response.status_code
        return response
    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        db = get_db()
        doc = {
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
            "status": status,
            "durationMs": duration_ms,
            "createdAt": __import__("datetime").datetime.utcnow(),
        }
        try:
            db.req_logs.insert_one(doc)
        except Exception:
            # don't crash the app if logging fails
            pass
