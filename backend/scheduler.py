import sys
from datetime import date
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, func

from config import LOOKBACK_DAYS
from db.database import init_db, get_session, Signal
from data.idx_symbols import fetch_all_idx_symbols
from data.fetcher import fetch_all
from analysis.indicators import compute_indicators
from analysis.scoring import score_indicators, label_from_score
from analysis.projection import calculate_projection
from tracker.result_tracker import run_evening_tracker

WIB = ZoneInfo("Asia/Jakarta")


def run_morning_analysis() -> None:
    today = date.today()

    # Idempotency: skip if signals already exist for today
    with get_session() as session:
        existing = session.execute(
            select(func.count(Signal.id)).where(Signal.date == today)
        ).scalar_one()
    if existing > 0:
        print(f"[morning] {existing} signals already exist for {today}. Skipping.")
        return

    print(f"[morning] Starting analysis for {today}...")
    symbols = fetch_all_idx_symbols()
    print(f"[morning] Fetching OHLCV for {len(symbols)} symbols...")
    price_data = fetch_all(symbols, LOOKBACK_DAYS)
    print(f"[morning] Price data received for {len(price_data)} symbols.")

    created = skipped = 0
    batch: list[Signal] = []

    with get_session() as session:
        for symbol, df in price_data.items():
            try:
                ind = compute_indicators(df)
                if ind is None:
                    skipped += 1
                    continue

                score, breakdown, trade_type = score_indicators(ind)
                label = label_from_score(score)
                proj  = calculate_projection(ind, label)

                signal = Signal(
                    symbol=symbol,
                    date=today,
                    score=score,
                    signal_label=label,
                    trade_type=trade_type,
                    entry_price  = proj["entry"]       if proj else None,
                    target_price = proj["target"]      if proj else None,
                    stop_loss    = proj["stop_loss"]   if proj else None,
                    risk_reward  = proj["risk_reward"] if proj else None,
                    indicators={
                        "rsi":       ind.get("rsi"),
                        "macd_hist": ind.get("macd_hist"),
                        "ema20":     ind.get("ema20"),
                        "ema50":     ind.get("ema50"),
                        "adx":       ind.get("adx"),
                        "vol_ratio": ind.get("vol_ratio"),
                        "breakdown": breakdown,
                    },
                )
                batch.append(signal)
                created += 1

                if len(batch) >= 100:
                    _flush(session, batch)
                    batch = []

            except Exception as exc:
                print(f"[morning] Error on {symbol}: {exc}")
                skipped += 1

        if batch:
            _flush(session, batch)

    print(f"[morning] Done. {created} signals created, {skipped} skipped.")


def _flush(session, batch: list) -> None:
    try:
        session.add_all(batch)
        session.commit()
        batch.clear()
    except Exception as exc:
        session.rollback()
        print(f"[morning] Batch commit failed: {exc}")
        batch.clear()


def main() -> None:
    init_db()

    args = sys.argv[1:]

    if "--now" in args:
        run_morning_analysis()
        return

    if "--evening" in args:
        run_evening_tracker()
        return

    scheduler = BlockingScheduler(timezone=WIB)

    scheduler.add_job(
        run_morning_analysis,
        CronTrigger(hour=7, minute=0, day_of_week="mon-fri", timezone=WIB),
        id="morning_analysis",
        name="Morning signal analysis",
    )
    scheduler.add_job(
        run_evening_tracker,
        CronTrigger(hour=18, minute=0, day_of_week="mon-fri", timezone=WIB),
        id="evening_tracker",
        name="Evening result tracker",
    )

    print("[scheduler] Running. Jobs: 07:00 WIB (analysis) | 18:00 WIB (tracker) — weekdays only.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[scheduler] Stopped.")


if __name__ == "__main__":
    main()
