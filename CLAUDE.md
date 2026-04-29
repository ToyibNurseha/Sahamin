# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What this project is

**Sahamin** is a read-only stock signal dashboard for the Indonesian Stock Exchange (IDX). It has two halves:

- `backend/` — Python pipeline that fetches OHLCV data via yfinance, scores every IDX stock with a technical indicator vote system, stores results in SQLite, and serves them via FastAPI.
- `frontend/` — Next.js 14 App Router dashboard that displays the signals as a Bloomberg-style dark terminal UI.

There is **no live trading, no broker integration, no auth**.

---

## Running the project

### Backend

```bash
cd backend
source venv/bin/activate          # must be active for all commands below
python scheduler.py --now          # seed today's signals (takes ~2 min for 50 stocks)
python scheduler.py --evening      # run the WIN/LOSS evaluator manually
uvicorn api:app --reload --port 8000
```

The scheduler normally runs on cron at **07:00 WIB** (morning analysis) and **18:00 WIB** (evening tracker). Start it blocking with `python scheduler.py`.

### Frontend

```bash
cd frontend
npm run dev       # http://localhost:3000
npm run build     # production build + type-check
```

---

## Architecture

### Data flow (backend)

```
fetch_all_idx_symbols()          50 LQ45/KOMPAS100 tickers (IDX API 403s → fallback)
        ↓
data/fetcher.py                  yfinance batch download, 50/batch, 2 threads, 1.5s stagger
        ↓
analysis/indicators.py           ta library: RSI, MACD, EMA 20/50/200, Stoch, BB, ATR, ADX
        ↓
analysis/scoring.py              vote system → float score (–10 to +10) + breakdown dict + trade_type
        ↓
analysis/projection.py           ATR-based entry / target / stop / R:R  (null for HOLD)
        ↓
db/database.py Signal table      (symbol, date) unique — idempotent, safe to re-run
        ↓  (18:00 WIB)
tracker/result_tracker.py        WIN/LOSS evaluation → Result table
        ↓
api.py                           /signals /summary /history /health → frontend
```

### Scoring system

Seven indicators vote independently; scores sum to a float:

| Indicator    | Max weight |
|--------------|-----------|
| RSI          | ±2        |
| MACD hist    | ±2        |
| EMA 20/50    | ±1        |
| Bollinger    | ±1        |
| Stochastic   | ±1        |
| ADX (amp.)   | ±0.5      |
| Volume (amp.)| ±0.5      |

Thresholds in `config.py`: `SCORE_STRONG_BUY=5`, `SCORE_BUY=3`, `SCORE_SELL=-3`, `SCORE_STRONG_SELL=-5`.

### Database (SQLAlchemy 2.x, SQLite)

Two tables: `signals` and `results`. Unique constraint on `(symbol, date)` in signals. Results have a one-to-one FK back to signals. Sessions are always used as context managers (`with get_session() as session:`); all ORM object access happens inside the `with` block.

### Frontend components

Only `IndicatorBreakdown.tsx` is a client component (`'use client'`). Everything else — including `SignalCard` which imports `IndicatorBreakdown` — is a server component. Data fetching is done in `page.tsx` and `history/page.tsx` via `async/await` with `{ cache: 'no-store' }`.

URL state: the active label filter lives in `?label=STRONG+BUY`, forwarded to the backend as-is. Date defaults to today server-side if absent.

### Formatting conventions

- Prices use Indonesian locale (`toLocaleString('id-ID')`) → thousands separator is `.` not `,`
- All color helpers (`getSignalTextColor`, `getSignalBarColor`, `getResultBorderColor`, etc.) live in `frontend/src/app/lib/format.ts` and return complete Tailwind class strings — never dynamic string concatenation, so Tailwind's purge doesn't drop them.
- Left border color on `SignalCard` uses inline `style` (not a Tailwind class) to avoid CSS specificity conflicts between `border-color` shorthand and `border-left-color`.

---

## Key constraints

- **Backend API field names are fixed** — the frontend depends on exact field names (`signal_label`, `result_status`, `result_pct`, etc.). Don't rename them.
- **Symbol format**: stored as `BBCA.JK` in DB, `.JK` stripped in API responses.
- **`pandas-ta` is not available on PyPI** — replaced with the `ta` library (`ta==0.11.0`). Don't try to re-add it.
- **No UI libraries** — all components are built from scratch with Tailwind. No shadcn, no Radix.
- **HOLD signals** have null entry/target/stop prices and are rendered in a collapsed `<details>` block on the dashboard, not in the main grid.
