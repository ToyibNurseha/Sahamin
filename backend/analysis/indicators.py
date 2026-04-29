from typing import Optional

import numpy as np
import pandas as pd
import ta.momentum as tam
import ta.trend as tat
import ta.volatility as tav


def _f(val) -> Optional[float]:
    """Return float or None, collapsing NaN/Inf."""
    if val is None:
        return None
    try:
        f = float(val)
        return None if (np.isnan(f) or np.isinf(f)) else f
    except (TypeError, ValueError):
        return None


def compute_indicators(df: pd.DataFrame) -> Optional[dict]:
    if df is None or len(df) < 60:
        return None

    try:
        close  = df["Close"]
        high   = df["High"]
        low    = df["Low"]
        volume = df["Volume"]

        # ── EMAs ──────────────────────────────────────────────────────────────
        ema20  = tat.EMAIndicator(close, window=20).ema_indicator()
        ema50  = tat.EMAIndicator(close, window=50).ema_indicator()
        ema200 = tat.EMAIndicator(close, window=200).ema_indicator() if len(df) >= 200 else None

        # ── RSI ───────────────────────────────────────────────────────────────
        rsi_s = tam.RSIIndicator(close, window=14).rsi()

        # ── MACD ──────────────────────────────────────────────────────────────
        macd_ind  = tat.MACD(close, window_slow=26, window_fast=12, window_sign=9)
        macd_line = macd_ind.macd()
        macd_sig  = macd_ind.macd_signal()
        macd_hist = macd_ind.macd_diff()   # histogram = MACD − signal

        # ── Stochastic ────────────────────────────────────────────────────────
        stoch_ind = tam.StochasticOscillator(high, low, close, window=14, smooth_window=3)
        stoch_k   = stoch_ind.stoch()
        stoch_d   = stoch_ind.stoch_signal()

        # ── Bollinger Bands ───────────────────────────────────────────────────
        bb_ind    = tav.BollingerBands(close, window=20, window_dev=2)
        bb_upper  = bb_ind.bollinger_hband()
        bb_lower  = bb_ind.bollinger_lband()
        bb_mid    = bb_ind.bollinger_mavg()

        # ── ATR ───────────────────────────────────────────────────────────────
        atr_s = tav.AverageTrueRange(high, low, close, window=14).average_true_range()

        # ── ADX ───────────────────────────────────────────────────────────────
        adx_s = tat.ADXIndicator(high, low, close, window=14).adx()

        # ── Volume SMA ────────────────────────────────────────────────────────
        vol_sma   = volume.rolling(20).mean()
        vol_sma_v = _f(vol_sma.iloc[-1])
        vol_ratio = None
        if vol_sma_v and vol_sma_v > 0:
            vol_ratio = _f(float(volume.iloc[-1]) / vol_sma_v)

        return {
            "close":          _f(close.iloc[-1]),
            "prev_close":     _f(close.iloc[-2]),
            "atr":            _f(atr_s.iloc[-1]),
            "ema20":          _f(ema20.iloc[-1]),
            "ema50":          _f(ema50.iloc[-1]),
            "ema200":         _f(ema200.iloc[-1]) if ema200 is not None else None,
            "rsi":            _f(rsi_s.iloc[-1]),
            "macd":           _f(macd_line.iloc[-1]),
            "macd_signal":    _f(macd_sig.iloc[-1]),
            "macd_hist":      _f(macd_hist.iloc[-1]),
            "macd_hist_prev": _f(macd_hist.iloc[-2]),
            "stoch_k":        _f(stoch_k.iloc[-1]),
            "stoch_d":        _f(stoch_d.iloc[-1]),
            "bb_upper":       _f(bb_upper.iloc[-1]),
            "bb_lower":       _f(bb_lower.iloc[-1]),
            "bb_mid":         _f(bb_mid.iloc[-1]),
            "adx":            _f(adx_s.iloc[-1]),
            "vol_ratio":      vol_ratio,
            "volume":         int(volume.iloc[-1]) if _f(float(volume.iloc[-1])) is not None else None,
        }

    except Exception as exc:
        print(f"[indicators] Computation error: {exc}")
        return None
