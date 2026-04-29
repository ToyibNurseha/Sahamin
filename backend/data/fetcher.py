import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

import pandas as pd
import yfinance as yf

from config import LOOKBACK_DAYS

_MIN_ROWS = 60
_BATCH_SIZE = 50
_MAX_WORKERS = 2   # keep low to avoid Yahoo rate-limiting
_MAX_RETRIES = 3
_BATCH_DELAY = 1.5  # seconds between batch submissions


def _date_range(period_days: int):
    end = pd.Timestamp.today().normalize()
    start = end - pd.Timedelta(days=period_days)
    return start, end


def _download_batch(symbols: List[str], period_days: int, attempt: int = 0) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    start, end = _date_range(period_days)

    try:
        if len(symbols) == 1:
            df = yf.download(symbols[0], start=start, end=end, auto_adjust=True, progress=False, threads=False)
            if not df.empty and len(df) >= _MIN_ROWS:
                results[symbols[0]] = df
        else:
            data = yf.download(
                symbols, start=start, end=end,
                group_by="ticker", auto_adjust=True, progress=False, threads=False,
            )
            for sym in symbols:
                try:
                    df = data[sym].dropna(how="all")
                    if len(df) >= _MIN_ROWS:
                        results[sym] = df
                except Exception:
                    pass

    except Exception as exc:
        if attempt < _MAX_RETRIES:
            time.sleep(2 ** attempt)
            return _download_batch(symbols, period_days, attempt + 1)
        print(f"[fetcher] Batch failed after {_MAX_RETRIES} retries: {exc}")

    return results


def _batches(lst: List, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def fetch_all(symbols: List[str], period_days: int = LOOKBACK_DAYS) -> Dict[str, pd.DataFrame]:
    all_data: Dict[str, pd.DataFrame] = {}
    batch_list = list(_batches(symbols, _BATCH_SIZE))

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
        futures = {}
        for i, batch in enumerate(batch_list):
            if i > 0:
                time.sleep(_BATCH_DELAY)
            futures[pool.submit(_download_batch, batch, period_days)] = batch

        for future in as_completed(futures):
            try:
                all_data.update(future.result())
            except Exception as exc:
                print(f"[fetcher] Future error: {exc}")

    return all_data


def fetch_today(symbols: List[str]) -> Dict[str, pd.DataFrame]:
    return fetch_all(symbols, period_days=5)
