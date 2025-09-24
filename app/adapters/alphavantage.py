import os, requests

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
BASE = "https://www.alphavantage.co/query"

class AlphaVantageError(Exception):
    pass

def fetch_global_quote(symbol: str):
    if not API_KEY:
        raise AlphaVantageError("Missing ALPHAVANTAGE_API_KEY in environment.")
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": API_KEY}
    r = requests.get(BASE, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if "Note" in data:
        # rate limit message
        raise AlphaVantageError("Alpha Vantage rate limit hit. Try again in a minute.")
    if "Global Quote" not in data or not data["Global Quote"]:
        raise AlphaVantageError(f"No quote returned for symbol '{symbol}'.")
    return data["Global Quote"]
