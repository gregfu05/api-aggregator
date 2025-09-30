from fastapi import APIRouter
from app.db.mongo import get_db

router = APIRouter()

@router.get("/logs/status")
def logs_status():
    db = get_db()
    c = db.req_logs.count_documents({})
    latest = db.req_logs.find({}, {"_id":0}).sort("createdAt", -1).limit(3)
    return {"count": c, "latest": list(latest)}
