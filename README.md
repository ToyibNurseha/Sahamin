# Sahamin 📈

A read-only stock signal dashboard for the **Indonesian Stock Exchange (IDX)**. Sahamin scores every stock in the LQ45/KOMPAS100 universe with a technical indicator vote system and presents the results as a Bloomberg-style dark terminal UI.

> No live trading. No broker integration. No auth.

---

## How it works

```
IDX Symbols (LQ45 / KOMPAS100)
        ↓
yfinance OHLCV data
        ↓
Technical Indicators  →  RSI · MACD · EMA · Bollinger · Stochastic · ADX · Volume
        ↓
Vote-based Score  (–10 to +10)
        ↓
Signal Label  →  STRONG BUY · BUY · HOLD · SELL · STRONG SELL
        ↓
ATR-based Trade Plan  →  Entry · Target · Stop Loss · R:R
        ↓
SQLite  →  FastAPI  →  Next.js Dashboard
        ↓  (18:00 WIB)
WIN / LOSS evaluator
```

### Scoring system

Seven indicators vote independently; their scores sum to a float in the range **–10 to +10**.

| Indicator       | Max weight |
|-----------------|:----------:|
| RSI             | ±2         |
| MACD histogram  | ±2         |
| EMA 20/50       | ±1         |
| Bollinger Bands | ±1         |
| Stochastic      | ±1         |
| ADX (amplifier) | ±0.5       |
| Volume (amplifier) | ±0.5    |

| Score threshold | Label         |
|-----------------|---------------|
| ≥ 5             | STRONG BUY    |
| ≥ 3             | BUY           |
| ≤ –3            | SELL          |
| ≤ –5            | STRONG SELL   |
| otherwise       | HOLD          |

---

## Tech stack

| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Data      | yfinance, pandas, ta                            |
| Backend   | Python 3, FastAPI, SQLAlchemy 2.x, SQLite       |
| Scheduler | APScheduler (07:00 WIB analysis · 18:00 WIB tracker) |
| Frontend  | Next.js 14 (App Router), TypeScript, Tailwind CSS |

---

## Project structure

```
sahamin/
├── backend/
│   ├── api.py                  # FastAPI app — /signals /summary /history /health
│   ├── config.py               # Score thresholds & constants
│   ├── scheduler.py            # APScheduler + CLI flags (--now, --evening)
│   ├── analysis/
│   │   ├── indicators.py       # ta library wrappers
│   │   ├── scoring.py          # vote system → score + label + trade_type
│   │   └── projection.py       # ATR-based entry / target / stop / R:R
│   ├── data/
│   │   ├── fetcher.py          # yfinance batch download
│   │   └── idx_symbols.py      # LQ45 / KOMPAS100 ticker list
│   ├── db/
│   │   └── database.py         # SQLAlchemy models (Signal, Result)
│   └── tracker/
│       └── result_tracker.py   # Evening WIN/LOSS evaluator
└── frontend/
    └── src/app/
        ├── page.tsx            # Main signal dashboard
        ├── history/page.tsx    # Historical results
        └── components/         # SignalCard, FilterTabs, SummaryBar, …
```

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Seed today's signals (~2 min for 50 stocks)
python scheduler.py --now

# Start the API
uvicorn api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

#### Scheduled jobs (optional)

Start the blocking scheduler to run automatically on cron:

```bash
python scheduler.py
# 07:00 WIB — morning analysis
# 18:00 WIB — evening WIN/LOSS tracker
```

Or trigger each job manually:

```bash
python scheduler.py --now       # run morning analysis immediately
python scheduler.py --evening   # run WIN/LOSS evaluator immediately
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

---

## API endpoints

| Method | Path        | Description                              |
|--------|-------------|------------------------------------------|
| GET    | `/signals`  | Signals for a given date, with optional label filter |
| GET    | `/summary`  | Count of each signal label for a date   |
| GET    | `/history`  | Paginated historical results             |
| GET    | `/health`   | Health check                             |

Query params for `/signals`: `date` (ISO 8601), `label` (e.g. `STRONG BUY`), `limit`.

---

## License

MIT
