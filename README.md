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
-  **Comprehensive backend tests** using Pytest (75% coverage)  
-  **Prometheus metrics** for monitoring (request counts, latency, etc.)  
-  **CI/CD pipeline** with GitHub Actions & Docker Hub deployment

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
| `GET /metrics` | Prometheus metrics endpoint |

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

This project includes a comprehensive backend test suite (`tests/` folder) written in **Pytest** with **75% code coverage**.  
The tests mock external API calls (CoinGecko & Alpha Vantage) and use an in-memory fake database to simulate MongoDB, making them **CI/CD-friendly** (no real database required).

### Run Tests
```bash
pytest -q
```

### Run Tests with Coverage Report
```bash
pytest --cov=app --cov-report=term-missing
```

### Coverage Gate (CI/CD)
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=70
```

### Test Coverage Areas
- **API Routes**: `/health`, `/crypto/price`, `/stocks/quote`, `/aggregate`, `/assets`, `/suggest`, `/cache`, `/logs`
- **Web UI Routes**: `/`, `/crypto`, `/stocks`, `/ui/search`
- **Services**: Aggregator, cache service, assets service
- **Cache Logic**: hit/miss behavior, TTL expiration
- **History Endpoints**: `/history/crypto`, `/history/stock` (mocked 30-day data)
- **Request Logging**: Middleware functionality

### Test Structure
All tests run **without requiring MongoDB** thanks to:
- Mocked external APIs (CoinGecko, Alpha Vantage)
- In-memory fake database with MongoDB-like interface
- In-memory cache service
- Patches applied at pytest configuration time

### Example Output
```
$ pytest --cov=app --cov-report=term-missing -q
............................................................................
76 passed, 11 warnings in 1.54s

Name                             Stmts   Miss  Cover
--------------------------------------------------------------
TOTAL                              435    108    75%
```

---

## Monitoring & Metrics

This project exposes a **Prometheus-compatible metrics endpoint** using `prometheus-fastapi-instrumentator`.

### Metrics Endpoint
```
http://127.0.0.1:8000/metrics
```

This endpoint provides:
- **`http_requests_total`** – Number of requests per endpoint
- **Request duration histogram** – Response time distribution
- **Request/Response size** – Data transfer metrics
- **Python GC & runtime metrics** – Garbage collection and system stats

### Running Prometheus (Local)

The project includes a `prometheus.yml` configuration file. To start monitoring:

**1. Start Prometheus with Docker:**
```bash
docker run -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

**2. Open Prometheus UI:**
```
http://localhost:9090
```

**3. Query metrics** such as:
- `http_requests_total` – Total request count
- `http_request_duration_seconds_bucket` – Request latency
- `http_requests_created` – Request timestamps

**4. Test the metrics:**
Trigger endpoints like `/crypto`, `/stocks`, `/aggregate` and watch the request counters increase in Prometheus.

### Prometheus Configuration
The `prometheus.yml` file scrapes metrics from the FastAPI app every 5 seconds:

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "cryptostock"
    static_configs:
      - targets: ["host.docker.internal:8000"]
```

---

## CI/CD Pipeline

This repository includes a **full CI/CD workflow** configured in `.github/workflows/ci.yml` using **GitHub Actions** and **Docker Hub**.

### CI Stage: `test-and-build`

Every push to `main` or pull request triggers:

1. **Python setup** (Python 3.11)
2. **Dependency installation** (`pip install -r requirements.txt`)
3. **Pytest with coverage gate** (must be ≥ 70%)
4. **Docker build** to ensure Dockerfile correctness

**The workflow fails if:**
-  Tests fail
-  Coverage < 70%
-  Docker build fails

### CD Stage: `deploy`

If all tests pass, a second job deploys the Docker image to **Docker Hub**.

**Setup Requirements:**
- Repository secrets (Settings → Secrets and variables → Actions):
  - `DOCKERHUB_USERNAME` – Your Docker Hub username
  - `DOCKERHUB_TOKEN` – Docker Hub personal access token (not password!)

**Deployment Process:**
1. Logs into Docker Hub using secrets
2. Builds the Docker image with Buildx
3. Tags the image as `gregfu05/cryptostock-app:latest`
4. Pushes to Docker Hub

### Pull the Deployed Image

```bash
docker pull gregfu05/cryptostock-app:latest
```

### Run the Deployed Image

```bash
docker run -p 8000:8000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017 \
  -e MONGODB_DB=aggregator \
  -e ALPHAVANTAGE_API_KEY=your_key_here \
  gregfu05/cryptostock-app:latest
```

### View CI/CD Status

Check the workflow status at:
```
https://github.com/gregfu05/api-aggregator/actions
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
