from fastapi import APIRouter, HTTPException, Body, Query
from typing import Optional, Dict, Any
from app.services.assets_service import list_assets, add_asset, update_asset, delete_asset

router = APIRouter()

@router.get("/assets")
def get_assets():
    return list_assets()

@router.post("/assets")
def create_asset(symbol: str = Body(...), type: str = Body(...), name: Optional[str] = Body(None)):
    type_norm = type.lower()
    if type_norm not in ("crypto", "stock"):
        raise HTTPException(status_code=400, detail="type must be 'crypto' or 'stock'")
    return add_asset(symbol, type_norm, name)

@router.put("/assets")
def put_asset(symbol: str = Body(...), updates: Dict[str, Any] = Body(...)):
    if not updates:
        raise HTTPException(status_code=400, detail="no updates provided")
    doc = update_asset(symbol, updates)
    if not doc:
        raise HTTPException(status_code=404, detail="asset not found")
    return doc

@router.delete("/assets")
def remove_asset(symbol: str = Query(...)):
    deleted = delete_asset(symbol)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="asset not found")
    return {"deleted": deleted}
