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
