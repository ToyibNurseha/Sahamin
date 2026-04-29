from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from db.database import init_db, get_session, Signal, Result

app = FastAPI(title="IDX Insights API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_date(raw: Optional[str]) -> date:
    if not raw:
        return date.today()
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return date.today()


def _strip_jk(symbol: str) -> str:
    return symbol.removesuffix(".JK")


def _format_signal(sig: Signal) -> dict:
    r = sig.result
    return {
        "id":            sig.id,
        "symbol":        _strip_jk(sig.symbol),
        "date":          str(sig.date),
        "score":         sig.score,
        "signal_label":  sig.signal_label,
        "trade_type":    sig.trade_type,
        "entry_price":   sig.entry_price,
        "target_price":  sig.target_price,
        "stop_loss":     sig.stop_loss,
        "risk_reward":   sig.risk_reward,
        "indicators":    sig.indicators,
        "result_status": r.status     if r else None,
        "result_pct":    r.result_pct if r else None,
    }


# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/signals")
def get_signals(
    date:  Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    limit: int           = Query(200, ge=1, le=1000),
):
    target = _parse_date(date)

    with get_session() as session:
        stmt = (
            select(Signal)
            .options(joinedload(Signal.result))
            .where(Signal.date == target)
            .order_by(Signal.score.desc())
            .limit(limit)
        )
        if label:
            stmt = stmt.where(Signal.signal_label == label.upper())

        signals = session.execute(stmt).scalars().all()
        return [_format_signal(s) for s in signals]


@app.get("/summary")
def get_summary(date: Optional[str] = Query(None)):
    target = _parse_date(date)

    with get_session() as session:
        # Signal label counts
        label_rows = session.execute(
            select(Signal.signal_label, func.count(Signal.id))
            .where(Signal.date == target)
            .group_by(Signal.signal_label)
        ).all()
        counts = {lbl: cnt for lbl, cnt in label_rows}
        total  = sum(counts.values())

        # Result aggregates (WIN + LOSS only for P&L; OPEN counted separately)
        result_rows = session.execute(
            select(Result.status, func.count(Result.id), func.sum(Result.result_pct))
            .join(Signal, Result.signal_id == Signal.id)
            .where(Signal.date == target)
            .where(Result.status.in_(["WIN", "LOSS", "OPEN"]))
            .group_by(Result.status)
        ).all()

        has_results = bool(result_rows)
        wins = losses = 0
        cum_pnl = 0.0

        for status, cnt, pct_sum in result_rows:
            if status == "WIN":
                wins     = cnt
                cum_pnl += pct_sum or 0.0
            elif status == "LOSS":
                losses   = cnt
                cum_pnl += pct_sum or 0.0

        resolved  = wins + losses
        win_rate  = round(wins / resolved * 100, 1) if resolved > 0 else None

        return {
            "date":        str(target),
            "total":       total,
            "strong_buy":  counts.get("STRONG BUY", 0),
            "buy":         counts.get("BUY", 0),
            "hold":        counts.get("HOLD", 0),
            "sell":        counts.get("SELL", 0),
            "strong_sell": counts.get("STRONG SELL", 0),
            # These are null in the morning (no results yet)
            "wins":        wins     if has_results else None,
            "losses":      losses   if has_results else None,
            "win_rate":    win_rate if has_results else None,
            "cum_pnl":     round(cum_pnl, 2) if has_results else None,
        }


@app.get("/history")
def get_history(days: int = Query(30, ge=1, le=365)):
    cutoff = date.today() - timedelta(days=days)

    with get_session() as session:
        rows = session.execute(
            select(Result.date, Result.symbol, Result.status, Result.result_pct)
            .where(Result.date >= cutoff)
            .where(Result.status.in_(["WIN", "LOSS", "OPEN"]))
            .order_by(Result.date.desc())
        ).all()

    return [
        {
            "date":   str(r.date),
            "symbol": _strip_jk(r.symbol),
            "status": r.status,
            "pct":    r.result_pct,
        }
        for r in rows
    ]


@app.get("/health")
def health():
    try:
        with get_session() as session:
            session.execute(select(func.count(Signal.id))).scalar_one()
        return {"status": "ok", "db": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail={"status": "error", "db": "unreachable"})


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    uvicorn.run("api:app", host=API_HOST, port=API_PORT, reload=False)
