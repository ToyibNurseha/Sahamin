from datetime import date, datetime

from sqlalchemy import select, not_

from db.database import get_session, Signal, Result
from data.fetcher import fetch_today


def run_evening_tracker() -> None:
    today = date.today()

    with get_session() as session:
        already_tracked = select(Result.signal_id)
        stmt = (
            select(Signal)
            .where(Signal.date == today)
            .where(not_(Signal.id.in_(already_tracked)))
        )
        open_signals = session.execute(stmt).scalars().all()

    if not open_signals:
        print(f"[tracker] No open signals for {today}.")
        return

    symbols = list({s.symbol for s in open_signals})
    print(f"[tracker] Fetching today's OHLCV for {len(symbols)} symbols...")
    price_data = fetch_today(symbols)

    batch: list[Result] = []

    with get_session() as session:
        for sig in open_signals:
            result = _evaluate(sig, price_data, today)
            if result is None:
                continue
            batch.append(result)

            if len(batch) >= 50:
                session.add_all(batch)
                session.commit()
                batch = []

        if batch:
            session.add_all(batch)
            session.commit()

    print(f"[tracker] Done. {len(open_signals)} signals processed.")


def _evaluate(sig: Signal, price_data: dict, today: date):
    # HOLD signals — no entry price to evaluate
    if sig.signal_label == "HOLD" or sig.entry_price is None:
        _log(sig.symbol, "NO_ENTRY", 0.0)
        return Result(
            signal_id=sig.id,
            symbol=sig.symbol,
            date=today,
            entry_price=None,
            status="NO_ENTRY",
            result_pct=0.0,
            updated_at=datetime.utcnow(),
        )

    df = price_data.get(sig.symbol)
    if df is None or df.empty:
        print(f"[tracker] {sig.symbol}: no price data, skipping.")
        return None

    # Prefer rows dated today; fall back to last available row
    today_rows = df[df.index.normalize() == str(today)]
    row = today_rows.iloc[-1] if not today_rows.empty else df.iloc[-1]

    high  = float(row["High"])
    low   = float(row["Low"])
    close = float(row["Close"])
    entry  = sig.entry_price
    target = sig.target_price
    stop   = sig.stop_loss

    if sig.signal_label in ("BUY", "STRONG BUY"):
        if target is not None and high >= target:
            status, pct = "WIN",  _pct(target - entry, entry)
        elif stop is not None and low <= stop:
            status, pct = "LOSS", _pct(stop   - entry, entry)
        else:
            status, pct = "OPEN", _pct(close  - entry, entry)
    else:  # SELL / STRONG SELL
        if target is not None and low <= target:
            status, pct = "WIN",  _pct(entry - target, entry)
        elif stop is not None and high >= stop:
            status, pct = "LOSS", _pct(entry - stop,   entry)
        else:
            status, pct = "OPEN", _pct(entry - close,  entry)

    _log(sig.symbol, status, pct)
    return Result(
        signal_id=sig.id,
        symbol=sig.symbol,
        date=today,
        entry_price=entry,
        high_of_day=high,
        low_of_day=low,
        close_price=close,
        result_pct=pct,
        status=status,
        updated_at=datetime.utcnow(),
    )


def _pct(diff: float, entry: float) -> float:
    return round(diff / entry * 100, 2)


def _log(symbol: str, status: str, pct: float) -> None:
    sign = "+" if pct >= 0 else ""
    print(f"[tracker] {symbol}: {status} ({sign}{pct:.2f}%)")
