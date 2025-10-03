import requests


BASE = "https://api.coingecko.com/api/v3/simple/price"

def fetch_simple_price(ids, vs_currencies):
    params = {
        "ids": ",".join(ids),
        "vs_currencies": ",".join(vs_currencies)
    }
    r = requests.get(BASE, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


# for suggestions
import time
_coin_list_cache = {"items": [], "ts": 0}

def _fetch_coin_list():
    url = "https://api.coingecko.com/api/v3/coins/list?include_platform=false"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    # items look like: {"id":"bitcoin","symbol":"btc","name":"Bitcoin"}
    return r.json()

def get_coin_list_cached(max_age_sec: int = 6*3600):
    now = time.time()
    if not _coin_list_cache["items"] or now - _coin_list_cache["ts"] > max_age_sec:
        _coin_list_cache["items"] = _fetch_coin_list()
        _coin_list_cache["ts"] = now
    return _coin_list_cache["items"]

def suggest_crypto(prefix: str, limit: int = 10):
    prefix = prefix.lower().strip()
    if not prefix:
        return []
    items = get_coin_list_cached()
    # match by name or symbol starting with prefix
    matches = []
    for it in items:
        if it["name"].lower().startswith(prefix) or it["symbol"].lower().startswith(prefix):
            matches.append({
                "id": it["id"],           
                "symbol": it["symbol"].upper(),
                "name": it["name"]
            })
            if len(matches) >= limit:
                break
    return matches
