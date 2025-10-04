# CryptoStock – API Aggregator with FastAPI & MongoDB

## Overview
**CryptoStock** is a FastAPI-based web application that aggregates live cryptocurrency and stock market data into a single interface.  
It connects to **CoinGecko** (for crypto) and **Alpha Vantage** (for stocks), with caching implemented in **MongoDB** (via TTL indexes) to reduce API calls and improve performance.  
The project also includes a simple web UI where users can:
- Search for **crypto** prices
- Search for **stock** quotes
- Use a **mixed search** to compare both
- View **price history graphs** (30-day line charts)
- Manage results with **caching** (showing “miss” on first call, then “hit” within TTL)

---

## Features
-  **Crypto price search** using CoinGecko API  
-  **Stock quote search** using Alpha Vantage API  
-  **Mixed aggregator endpoint** for combined results  
-  **MongoDB caching** with TTL (hit/miss visible in UI & API)  
-  **UI with suggestions** (typeahead for crypto & stock symbols)  
-  **Price history charts** (30 days, rendered with Chart.js)  
-  **Request logging** in Mongo (with 7-day TTL)  
-  **Comprehensive backend tests** using Pytest (see `tests/` folder)

---

## Architecture
- **FastAPI** as the backend framework  
- **MongoDB** (running in Docker) for caching & logs  
- **Adapters** for each external API (CoinGecko, Alpha Vantage)  
- **Service layer** (aggregator & cache service) shared by API and UI  
- **Templates** (Jinja2 + Chart.js) for the web interface  
- **Tests** (Pytest) for backend verification with mocked APIs

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/gregfu05/api-aggregator.git
cd api-aggregator
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment variables
Create a `.env` file in the project root:

```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=aggregator
ALPHAVANTAGE_API_KEY=your_alpha_vantage_api_key_here
```

> Get a free Alpha Vantage API key at: https://www.alphavantage.co/support/#api-key

### 5. Run MongoDB with Docker
```bash
docker compose up -d
```
This starts MongoDB in a container named `aggregator-mongo`.

### 6. Initialize indexes (cache TTL + logs TTL)
```bash
python -m scripts.init_db
```

### 7. Start the FastAPI server
```bash
uvicorn app.main:app --reload
```
Access it at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Usage

### API Endpoints
| Endpoint | Description |
|-----------|--------------|
| `GET /health` | Check server status |
| `GET /crypto/price?ids=bitcoin&vs=usd` | Live crypto price |
| `GET /stocks/quote?symbol=AAPL` | Live stock quote |
| `GET /aggregate?symbols=bitcoin,AAPL&window=60` | Combine both with caching |
| `GET /cache/status` | Cache contents / status |
| `GET /logs/status` | Recent request logs |

**Interactive docs:**  
- Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Web UI
Visit:
- `/crypto` → crypto search (with suggestions + chart)  
- `/stocks` → stock search (with suggestions + chart)  
- `/` → mixed search for both crypto & stocks (with overlay chart)

The UI displays cache results: **miss** on first call, **hit** on repeat (within TTL).

---

## Tests

This project includes a complete backend test suite (`tests/` folder) written in **Pytest**.  
The tests mock external API calls (CoinGecko & Alpha Vantage) and use an in-memory cache to simulate MongoDB.

### Run Tests
```bash
pytest -q
```
or for more detailed insights
```bash
pytest -q -vv
```

### Test Coverage
- `/health` endpoint  
- `/aggregate` cache (hit/miss logic)  
- `/history/crypto` and `/history/stock` (mocked 30-day data)  
- In-memory caching system functionality  

### Example Output
```
$ pytest -q
....                                                                                        [100%]
4 passed in 2.5s
```

---

## Development Notes
- Mongo cache TTL configurable via `window` parameter (default 60s).  
- Request logs stored in Mongo with a 7-day TTL (`req_logs` collection).  
- Modular code structure: **adapters**, **services**, **routes**, **templates**, **tests**.  
- Git commits are meaningful and descriptive to track incremental progress.

---

## License
This project is for academic purposes at **IE University**.
